# -*- coding: UTF-8 -*-
import hashlib
import redis
import datetime
import time
import json
import os
import threading
from enum import Enum


def format_return_result(type, info):
    return {"result": type.lower(), "info": info}


class TaskRunResult(object):
    running = 0x41301
    completed = 0x0


class PlHash():
    MD5_KEY = "437b677a-75c7-4326-80b1-5e663cf2c5e2".encode('utf-8')

    @classmethod
    def encry_message(cls, message, user=""):
        m = hashlib.md5(cls.MD5_KEY)
        encry_content = str(message)
        if user:
            encry_content = encry_content + user
        m.update(encry_content.encode('utf-8'))
        str_md5 = m.hexdigest()
        return str_md5

    @classmethod
    def verify_encry_message(cls, str_md5, message, user=""):
        encry_content = str(message)
        if user:
            encry_content = encry_content + user
        m = hashlib.md5(cls.MD5_KEY)
        m.update(encry_content.encode("utf-8"))
        md5 = m.hexdigest()
        return str_md5 == md5


class RemoteCmd():
    cmd_type = {
        "report_tasks_definition": 1,
        "report_tasks_state": 2,
        "proxy_connect": {"ProxyIp": "", "PeoxyUser": ""},
        "run_task": {"request_user": "", "author": "", "task": ""},
        "stop_task": {"request_user": "", "author": "", "task": ""},
        "response": 200
    }

    WEB_USER_NAME = "web"
    SERVER_USER_NAME = "server"

    @classmethod
    def gen_remote_cmd(cls, cmd_type, request_content, source_ip, user, sync_list=""):
        now_time = str(datetime.datetime.now()).split(".")[0]
        request_md5 = PlHash.encry_message(cmd_type + str(request_content), user)
        remote_cmd = {
            "cmd_type": cmd_type,
            "request_content": request_content,
            "send_user": user,
            # 确保操作类型、请求内容、请求用户不能被更改
            "request_md5": request_md5,
            "source_ip": source_ip,
            "cmd_time": now_time,
            "sync_list": sync_list
        }
        return json.dumps(remote_cmd)

    @classmethod
    def get_cmd_content(cls, cmd_info):
        remote_cmd = json.loads(cmd_info)
        send_user = remote_cmd.get("send_user")
        request_content = remote_cmd.get("request_content")
        source_ip = remote_cmd.get("source_ip")
        request_md5 = remote_cmd.get("request_md5")
        cmd_type = remote_cmd.get("cmd_type")
        cmd_time = remote_cmd.get("cmd_time")
        if not send_user or not request_content or not request_md5 or not source_ip or not cmd_time:
            raise Exception("cmd %s error.", remote_cmd)
        if not PlHash.verify_encry_message(request_md5, cmd_type + str(request_content), send_user):
            raise Exception("md5 check error.")
        time_array = time.strptime(cmd_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(time_array))
        if (int(time.time()) - timestamp) > 60:
            raise Exception(f"cmd expire.")
        return remote_cmd


class RedisClient():
    _RECV_CMD_LIST_SERVER = "recv_cmd_list_server"  # 服务器接受命令list
    _RECV_CMD_LIST_WBE = "recv_cmd_list_web"  # web接受命令list
    _RECV_CMD_LIST_CLIENT = "recv_cmd_list_client"  # 客户端监听命令list
    _RESPONSE_CMD_LIST = "response_cmd_list"  # 各个组件接受同步回复list
    _PROXY_ACTIVE_STATE = "proxy_active_key"  # 代理是否或者
    _PROXY_STATE_INFO_KEY = "proxy_state_info_key"  # 各个客户端缓存计划任务状态信息key
    _SIGNAL_KEY = "signal_info_key"  # 各个客户端缓存计划任务状态信息key

    def __init__(self, redis_ip, redis_port):
        u''' socket_connection_time=socket_timeout=0.2 影响查询时可调'''
        conn_url = f"redis://:32198ac7-7590-4131-816a-51350869744d@{redis_ip}:{redis_port}"
        conn_pool = redis.ConnectionPool.from_url(conn_url, decode_responses=True, socket_connect_timeout=10)
        self.cache = redis.StrictRedis(connection_pool=conn_pool)
        self.cache.ping()

    @property
    def redis_cache(self):
        return self.cache

    def get_server_recv_cmd_list(self):
        return self._RECV_CMD_LIST_SERVER

    def get_web_recv_cmd_list(self):
        return self._RECV_CMD_LIST_WBE

    def get_client_recv_cmd_list(self, proxy_id):
        client_cmd_list = self._RECV_CMD_LIST_CLIENT + "_" + proxy_id.lower()
        return client_cmd_list

    # uuid保证唯一
    def get_response_cmd_list(self, ip, user, uuid=False):
        response_cmd_list = self._RESPONSE_CMD_LIST + "_" + ip + "_" + user.lower()
        if uuid:
            pid = os.getpid()
            t = threading.currentThread()
            tid = t.ident
            response_cmd_list = response_cmd_list + "_" + str(pid) + "_" + str(tid) + "_" + str(time.time())
        return response_cmd_list

    def send_request_info(self, send_list, cmd_info):
        self.cache.lpush(send_list, cmd_info)

    def send_response_info(self, reponse_list, cmd_info, timeout=10):
        self.cache.lpush(reponse_list, cmd_info)
        self.cache.expire(reponse_list, timeout)

    def send_sync_request_info(self, response_list, send_list, cmd_info, timeout=10):
        self.cache.delete(response_list)
        self.cache.lpush(send_list, cmd_info)
        result = self.listen_cmd_list(response_list, timeout)
        return result

    def listen_cmd_list(self, listen_list, timeout=100):
        result = self.cache.blpop(listen_list, timeout=timeout)
        if result:
            return result[1]

    # 防止之前产生的命令回复，没有取，影响后续
    def clean_list(self, list):
        self.cache.delete(list)

    def set_key_value(self, key, value, expire_time):
        if not expire_time:
            self.cache.set(key, value)
        else:
            self.cache.set(key, value, ex=expire_time)

    def get_key_value(self, key):
        return self.cache.get(key)

    def mget_key(self, key_list):
        return self.cache.mget(key_list)

    def get_signal_key(self, signal):
        key = self._SIGNAL_KEY + "_" + signal
        return key

    def get_proxy_state_key(self, proxy_id):
        key = self._PROXY_STATE_INFO_KEY + "_" + proxy_id.lower()
        return key