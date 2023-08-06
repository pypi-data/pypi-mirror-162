from contextlib import ContextDecorator
import threading
from queue import PriorityQueue, Empty
import time
import os
from os import path
import shutil
import random
import pickle
import logging as log
import concurrent.futures
import itertools
from functools import partial
from concurrent.futures import Future
import example_demo.utils.redis_client as redis_c
from example_demo.utils.event_emitter import EventEmitter
from example_demo.utils.actor_message import ActorMessage
from example_demo.utils._constants import _HUB_URL
from example_demo.utils.util_fun import new_uuid, get_user, _now, get_ip, _from_timestamp, objectview
from example_demo.utils.startup_info import StartupInfo
from example_demo.utils.jobctl_util import AgentState, MachineState, remove_prefix, Script, PoolState, ProcessState, TaskState, TaskObject
from example_demo.utils.submit import Submit

# from jobctl_util import MachineState,remove_prefix,AgentState,Script,PoolState,ProcessState,TaskState,TaskObject
# from submit import Submit
# from startup_info import StartupInfo
# from util_fun import new_uuid, get_user, _now, get_ip, _from_timestamp, objectview
# from _constants import _HUB_URL
# from event_emitter import EventEmitter
# from actor_message import ActorMessage

flatten = itertools.chain.from_iterable




def _as_df(data, fields=None):
    u''' 尝试转为dataframe '''
    try:
        import pandas as pd
        return pd.DataFrame(data=data, columns=fields)
    except: # pylint: disable=bare-except
        return data

def _make_dataframe(tasks, fields):
    columns = {}
    for f in fields:
        for task in tasks:
            v = getattr(task, f)
            if f not in columns:
                columns[f] = [v]
            else:
                columns[f].append(v)
    return _as_df(columns, fields=fields)


class _Call(object):

    def __init__(self, sn, time, on_reply):
        self.sn = sn
        self.time = time
        self.on_reply = on_reply

    def __lt__(self, rhs):
        return self.time < rhs.time


class _CallManager(object):

    def __init__(self):
        self.calls = PriorityQueue()
        self.index = dict()

    def add(self, target, prefix, payload, on_reply, timeout, sn):
        call = _Call(sn=sn, time=time.time() + timeout, on_reply=on_reply)
        self.calls.put(call)
        self.index[sn] = call

    def remove(self, sn):
        return self.index.pop(sn, None)

    def expired_calls(self):
        expired_calls = []
        max_wait_time = 1
        now = time.time()
        while True:
            try:
                call = self.calls.get(False)
                max_wait_time = call.time - now
                if max_wait_time <= 0.:
                    call = self.index.pop(call.sn, None)
                    if call:
                        expired_calls.append(call)
                    continue
                self.calls.put(call)
                break
            except Empty:
                break
        return expired_calls, max_wait_time


def _decode_message(data):
    message = ActorMessage()
    message.ParseFromString(data)
    return (message.sender, message.prefix, message.payload, message.target, message.sn)

class Actor(EventEmitter, ContextDecorator):
    u''' Actor是一个处理消息的对象。
    每个Actor有一个唯一标识，该标识也是该Actor的接口队列的标识。
    '''

    @classmethod
    def _secure_url(cls, url):
        if not url.startswith('redis://:'):
            passwd = 'b840fc02d524045429941cc15f59e41cb7be6c52'
            url = f'redis://:{passwd}@' + url[8:]
        return url

    @classmethod
    def make_sn(cls, url, key):
        u''' 生成一个序列号  '''
        url = cls._secure_url(url)
        r = redis_c.from_url(url)
        return int(r.hincrby(key, '_SN'))

    def __init__(self, url, id):
        u'''
        Actor可以有两个收件箱: 自身的收件箱和自己所属的组的收件箱。
        '''
        super(Actor, self).__init__()
        self._url = Actor._secure_url(url)
        self.redis = redis_c.from_url(self._url)
        self.id = id
        # 当没有订阅任务消息时即退出消息循环，结束战斗。
        self._mbox = f'{id}:mbox'
        self._channels = [self._mbox]
        # 可动态调整的各类订阅各消息
        self.subscriptions = {}
        self.calls = _CallManager()
        self.idles = []
        self.is_running = False
        self._intervals = dict()
        self._bufsize = 10000
        self._req_sn_it = iter(range(0, 0))
        self._thread = threading.Thread(target=self._message_loop)

    def _next_req_sn(self):
        u''' 获取下一个流水号，避免重启消息后从1开始编号，导致序列号错乱。 '''
        try:
            return next(self._req_sn_it)
        except StopIteration:
            cur = int(self.redis.incrby("::req-sn", self._bufsize)) - self._bufsize
            if cur == 0:
                cur = 1
            self._req_sn_it = iter(range(cur, cur + self._bufsize))
        return next(self._req_sn_it)

    def unsubscribe_notify(self, channel):
        u''' 暂停订阅某个列表的数据 '''
        log.debug("unsubscribe notify: %s", channel)
        self.subscriptions.pop(channel, None)
        channels = [self._mbox]
        for channel in self.subscriptions:
            channels.append(channel)
        self._channels = channels

    def subscribe_notify(self, channel, callback):
        u''' 开始订阅某个列表的数据 '''
        log.debug("subscribe_notify: %s.", channel)
        self.subscriptions[channel] = callback
        channels = [self._mbox]
        for channel in self.subscriptions:
            channels.append(channel)
        self._channels = channels

    def start(self):
        u'''启动'''
        self.is_running = True
        self._thread.start()

    def stop(self):
        u'''停止'''
        self.is_running = False
        self._send(self.id, '', b'', self.id, -1, 1)
        if self._thread.ident != threading.get_ident():
            self._thread.join()

    def _message_loop(self):
        log.debug('%s started', self.id)
        try:
            # 清空已有队列
            try:
                self.redis.delete(f'{self.id}:mbox')
            except:
                pass
            self.on_setup()
        except:
            log.exception("call on_setup fail.")
            log.debug('%s exiting', self.id)
            self.on_teardown()
            self.emit('exit')
            return

        while self.is_running:
            expired_calls, max_wait_time = self.calls.expired_calls()
            for call in expired_calls:
                call.on_reply("timeout", None)

            data = self._recv(self._channels, max_wait_time)
            if data:
                channel, message = data[0].decode(), data[1]
                if channel != self._mbox:
                    fn = self.subscriptions.get(channel)
                    if fn:
                        try:
                            fn(message)
                        except:
                            log.exception("process channel(%s) message fail.", channel)
                    continue

                sender, prefix, payload, target, sn = _decode_message(message)
                if sn == -1:
                    continue

                if sn == 0 or sn is None:
                    log.debug('msg: %s <- %s: %s', target, sender, prefix)
                    self.on_message(sender, prefix, payload, target)
                    continue

                if prefix.endswith('-req'):  # pylint: disable=no-member
                    log.debug('req: %s <= %s: %s(%s)', target, sender, prefix, sn)
                    prefix = prefix[:-4]  # pylint: disable=unsubscriptable-object
                    method_name = f"_on_{prefix}_req"
                    fn = getattr(self, method_name, None)
                    if fn:
                        try:
                            fn(sender, prefix, payload, target, sn)
                        except Exception as ex:
                            log.exception('req: %s <= %s: %s(%s)', target, sender, prefix, sn)
                            self._send(sender, f"error", f"{target} exception: {ex}".encode(), self.id, sn, None)
                    else:
                        self._send(sender, f"error", f"no such request({prefix}) handler on {target}".encode(), self.id,
                                   sn, None)
                else:
                    log.debug('rep: %s <= %s: %s(%s)', target, sender, prefix, sn)
                    call = self.calls.remove(sn)
                    if call:
                        call.on_reply(prefix, payload)
                    else:
                        log.warning("discard reply %s(%s) from %s", prefix, sn, sender)
            else:
                # TODO: 设置一个idle调用的时机
                if not expired_calls:
                    for idle in self.idles:
                        idle()

        log.debug('%s exiting', self.id)
        self.on_teardown()
        self.emit('exit')

    def on_message(self, sender, prefix, payload, target):
        log.warning("msg: %s <- %s: %s discard", target, sender, prefix)

    def on_setup(self):
        pass

    def on_teardown(self):
        pass

    def send(self, target, prefix, payload, sender=None, timeout=60):
        u''' 向target发送消息 '''
        sender = sender or self.id
        log.debug('msg: %s -> %s: %s', sender, target, prefix)
        self._send(target, prefix, payload, sender, None, timeout)

    def call(self, target, prefix, payload, on_reply, timeout=10):
        u''' 调用target的prefix功能。默认超时时间为3秒。'''
        sn = self._next_req_sn()
        self.calls.add(target, prefix, payload, on_reply, timeout, sn)
        log.debug('req: %s => %s: %s(%d)', self.id, target, prefix, sn)
        return self._send(target, f"{prefix}-req", payload, self.id, sn, timeout=60)

    def async_call(self, target, prefix, payload=None, timeout=10):
        future = Future()

        def cb(prefix, payload):
            if prefix == 'error':
                future.set_exception(Exception(payload.decode()))
            else:
                future.set_result((prefix, payload))

        self.call(target, prefix, payload, cb, timeout=timeout)
        return future

    def reply(self, target, sn, prefix, payload):
        u''' 给target发送对请求id的应答。'''
        log.debug('rep: %s => %s: %s(%d)', self.id, target, prefix, sn)
        self._send(target, prefix, payload, self.id, sn, timeout=30)

    def defer(self, callable, delay=0):
        u''' 延时执行 '''
        sn = self._next_req_sn()
        self.calls.add(None, None, None, lambda prefix, payload: callable(), delay, sn)

    def interval(self, id, callable, span):
        u''' 周期性执行 '''
        self._intervals[id] = span

        def _fn():
            if id in self._intervals:
                # log.debug('%s: interval task %s trigger.', self.id, id)
                try:
                    callable()
                except:
                    log.exception('%s> call %s interval function fail.', self.id, id)
                    pass
                self.defer(_fn, span)

        self.defer(_fn, span)

    def stop_interval(self, id):
        self._intervals.pop(id, None)

    def on_idle(self, callable):
        u''' 增加一个actor空闲时调用的命令 '''
        self.idles.append(callable)

    def exit(self):
        u''' actor 正常退出. '''
        self.is_running = False

    @redis_c.auto_retry
    def _send(self, target, prefix, payload, sender, sn, timeout):
        target = f'{target}:mbox'
        message = ActorMessage(
            sender=sender, target=target, prefix=prefix, payload=payload or b'', sn=sn or 0).SerializeToString()
        # 30秒没有人接收则自动超时
        with self.redis.pipeline() as tx:
            tx.multi()
            tx.rpush(target, message)
            if timeout:
                tx.expire(target, timeout)
            tx.execute()

    @redis_c.auto_retry
    def _recv(self, ids, timeout):
        timeout = int(timeout)
        if timeout <= 1:
            timeout = 1
        try:
            return self.redis.blpop(ids, timeout=timeout)
        except KeyboardInterrupt:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

class JobCtl(Actor):
    u'''
    作业提交、进度查询、作业取消等用户控制命令。
    '''
    def __init__(self, url=None, ip=None, token=None):
        '''
        如果指定ip，则使用ip认证。否则取当前系统用户。
        '''
        url = os.environ.get(_HUB_URL) or url
        if url == "redis://192.168.5.42":
            url = "redis://sh-dpool"
        assert url, "Expect %s" % (url)
        self.url = url
        if ip is None:
            self.user = get_user()
            if self.user.endswith('$'):
                log.warning("不允许使用系统账户运行，请使用ip参数。")
                raise Exception("不允许使用系统账户运行，请使用ip参数。")
            self.ip = get_ip()
        else:
            self.user = None
            self.ip = ip
            self.token = token

        super(JobCtl, self).__init__(url, new_uuid('c'))
        self.start()
        self._auth()

    def _auth(self):
        u''' 进行认证 '''
        if not self.user:
            # Too naive.
            raw = self.redis.hget('::options', 'admin')
            if raw:
                if raw.decode() != self.token:
                    return False
            raw = self.redis.hget('::auth_ip', self.ip)
            if not raw:
                log.warning("Invalid ip: %s.", self.ip)
                return False
            self.user = raw.decode()

        self._uid = f'u-{self.user}'
        self.startup_info = StartupInfo.read_from_redis(self.redis, self.user)
        return True

    def _check_auth(self, user, ip):
        self.redis.sismember(f'{self._uid}:ip', self.ip)

    def select_jupyter_server(self):
        agents = self.agents
        if not agents:
            log.warning('分配jupyter服务器失败，一个代理都没有。')
            return
        i = random.randint(0, len(agents) - 1)
        server = remove_prefix(agents[i], f'a-{self.user}-')
        log.info('分配jupyter服务器: %s', server)
        self.redis.hset(self._uid, 'jupyter_server', server)
        self.startup_info = self.startup_info.set_jupyter_server(server)

    @property
    def mode(self):
        ''' 从redis中获取当前用户的启动模型，是以服务启动还是本地启动 '''
        raw = self.redis.hget(self._uid, 'mode')
        return raw is None and 'service' or 'ps'

    @property
    def work_dir(self):
        return self.startup_info.work_dir

    @property
    def custom_zone(self):
        return self.startup_info.custom_zone

    @property
    def system_zone(self):
        return self.startup_info.system_zone

    @property
    def jupyter_ip(self):
        return self.startup_info.jupyter_server

    @property
    def jupyter_port(self):
        return self.startup_info.jupyter_port

    @property
    def jupyter_url(self):
        return self._config_jupyter()

    @property
    def jupyter_pid(self):
        return f'p-{self.user}-jupyter'

    def submit(self, manifest):
        u'''
        根据清单文件提交作业。
        '''
        submit = Submit.from_manifest(manifest,
                                      custom_zone=self.custom_zone,
                                      system_zone=self.system_zone)
        self._submit(submit)
        print("作业提交成功: %s，工作目录: %s" % (submit.name, submit.prefix))

    def submit_pyfile(self, mainpy, name=None, files=[]):
        u'''
        提交python脚本，这种情况下不需要编写manifest.yaml.
        '''
        submit = Submit.make(mainpy,
                             name=name,
                             files=files,
                             custom_zone=self.custom_zone,
                             system_zone=self.system_zone)
        try:
            name = self._submit(submit)
            print("作业提交成功: %s，工作目录: %s" % (name, self.pwd(name)))
            return name
        finally:
            submit.clean_temps()

    def _is_running(self, name):
        s = self._state(name)
        if s is None:
            return False
        return s.state in {'submit', 'running'}

    def _submit(self, submit: Submit):
        # 任务正在运行，禁止上传脚本，否则会导致工作区文件混乱。
        if self._is_running(submit.name):
            raise Exception("Duplicated job: %s" % submit.name)

        job_dir = path.join(self.work_dir, 'job', submit.name)
        job_stdout_path = path.join(job_dir, 'stdout.txt')
        job_output_path = path.join(job_dir, 'output')
        try:
            os.unlink(job_stdout_path)
            shutil.rmtree(job_output_path)
        except:  # pylint: disable=bare-except
            pass

        submit.check_files()
        submit.upload_files()
        submit.write_submit_id()
        state, msg = self._submit_script(submit.name)
        if state:
            return submit.name
        raise Exception(msg)

    def _list_agents(self):
        agents = [AgentState.load(self.redis, agent) for agent in self.agents]
        return _make_dataframe(agents, [
            "ip", "pid", "mem_private", "cpu_percent",
            "num_children", "wd", "id", "uptime", "downtime", "timestamp"
        ])

    def list_agents(self):
        u''' 查看当前用户启动的用户代理进程。'''
        return self._list_agents()

    def list_scripts(self):
        u''' 显示用户已提交的作业状态信息。 '''
        scripts = self._list_scripts()
        return _make_dataframe(scripts, [
            "name", "state", "agent", "pid", "cost", "mem_private",
            "cpu_percent", "wd", "cmd", "current",
            "cs_queue", "cs_total", "cs_running", "cs_cost", "cs_estimate",
            "exit_time", "state_msg", "id", "create_time", "start_time", "timestamp"
        ])

    def list_machines(self):
        machines = [MachineState.load(self.redis, id) for id in self.machines]
        return _make_dataframe(machines, [
            "name", "ip", "mem_usage", "cpu_usage", "mem", "num_cores",
            "timestamp"
        ])

    def _list_scripts(self):
        raw = self.redis.smembers(f'{self._uid}:scripts')
        scripts = []
        for item in raw:
            id = item.decode()
            script = Script.from_id(self.redis, id)
            scripts.append(script.state)
        return scripts

    def _list_pools(self, script_id=None):
        if script_id:
            if not script_id.startswith('s-'):
                script_id = f's-{self.user}-{script_id}'
            raw = self.redis.smembers(f'{script_id}:pools')
        else:
            raw = self.redis.smembers(f'{self._uid}:pools')
        pools = {i.decode() for i in raw}
        return pools

    def list_jobs(self, script_id=None):
        u'''
        显示当前正在运行的任务。
        '''
        pools = [
            PoolState.load(self.redis, pool)
            for pool in self._list_pools(script_id=script_id)
        ]
        return _make_dataframe(pools, [
            'id', 'cost', 'eta', 'total', 'pending', 'running',
            'parallels', 'finished', 'failed', 'create_time'
        ])

    def clean(self, *names):
        u'''清理作业的工作目录。'''
        for name in names:
            name = path.basename(name)
            job_dir = path.join(self.work_dir, 'job', name)
            print("删除作业目录:", job_dir)
            if not path.exists(job_dir):
                continue
            shutil.rmtree(job_dir)

    @property
    def users(self):
        raw = self.redis.smembers('::users')
        return {user.decode() for user in raw}

    def list_all_agents(self):
        u'''
            每个用户的代理内存占用、代理状态统计信息等
        '''
        def list_all_agents():
            for user in self.users:
                user = remove_prefix(user, 'u-')
                for agent in self.redis.keys(f'a-{user}-*'):
                    agent = agent.decode()
                    if agent.find(':') == -1:
                        a = AgentState.load(self.redis, agent)
                        a.user = user
                        yield a
        return _make_dataframe(list(list_all_agents()), [
            "user", "ip", "pid", "mem_private", "cpu_percent",
            "num_children", "uptime", "downtime", "timestamp"
        ])

    def list_users(self):
        u''' 列举当前系统内的用户信息. '''
        return _as_df({'user': list(self.users)})

    @property
    def processes(self):
        for agent in self.agents:
            for pid in self.redis.smembers(f'{agent}:procs'):
                yield pid.decode()

    def list_processes(self):
        u''' 列举所有进程。'''
        processes = [
            ProcessState.load(self.redis, proc) for proc in self.processes
        ]
        return _make_dataframe(processes, [
            'id', 'state', 'agent', 'wd', 'create_time', 'cpu_percent',
            'mem_private', 'num_children', 'finish', 'fail', 'running',
            'timestamp', 'pid', 'cmd'
        ])

    def _state(self, name):
        script = Script.from_name(self.redis, self.user, name)
        return script.state

    def _watch(self, name, fn):
        def get_state(name):
            s = self._state(name)
            if s is None:
                return u'你的任务不见了。'
            state = s.state

            if (state == TaskState.RUNNING or state == TaskState.SUBMIT):
                time.sleep(1)
                return None
            elif state == TaskState.FAIL:
                return u'任务执行失败。'
            elif state == TaskState.FINISH:
                cost = s.cost
                return u'任务已结束，用时%s。' % str(cost)
            else:
                return "未知状态。"

        fp = None
        while True:
            try:
                fp = open(fn, 'r')
                break
            except Exception:
                s = get_state(name)
                if s:
                    yield s
                    break
                else:
                    continue

        while fp:
            new = fp.readline()
            if new:
                yield new
            else:
                s = get_state(name)
                if s:
                    yield s
                    break
                else:
                    continue

    def pwd(self, name):
        u''' 返回作业的工作目录。 '''
        name = path.basename(name)
        job_dir = path.join(self.work_dir, 'job', name)
        return job_dir

    def _exists(self, name):
        u''' 判定指定作业是否存在 '''
        script_id = Script.make_id(self.user, name)
        return self.redis.sismember(f'u-{self.user}:scripts', script_id)

    def log(self, name, watch=True, break_cancel=False):
        u''' 将作业的标准输出打印到控制台。 '''
        if not self._exists(name):
            print("无效的作业名:", name)
            return

        name = path.basename(name)
        job_dir = path.join(self.work_dir, 'job', name)
        print("作业目录:", job_dir)
        if not path.exists(job_dir):
            print("无效的作业名:", name)
            return

        job_stdout_path = path.join(job_dir, 'stdout.txt')
        if watch:
            # 如果监视输出，则在任务未结束之前，一直监视文件是否发生变化。
            try:
                for line in self._watch(name, job_stdout_path):
                    print(line, end='')
            except KeyboardInterrupt:
                if break_cancel:
                    self.kill_script(name)
                    print("任务已取消。")
                else:
                    pass
        else:
            with open(job_stdout_path, 'r') as lines:
                for line in lines:
                    print(line)

    def run(self, manifest):
        u'''
        根据清单文件执行作业。
        '''
        submit = Submit.from_manifest(manifest,
                                      custom_zone=self.custom_zone,
                                      system_zone=self.system_zone)
        try:
            self._submit(submit)
        except Exception as ex:
            print("提交作业失败:%s" % ex)
            return
        self.log(submit.name, break_cancel=True)

    def run_pyfile(self, mainpy, name=None, files=[]):
        u'''
        执行一个python脚本。
        '''
        submit = Submit.make(mainpy, name=name, files=files, custom_zone=self.custom_zone, system_zone=self.system_zone)
        try:
            self._submit(submit)
        except: # pylint: disable=bare-except
            log.exception("提交作业失败:%s", mainpy)
            return
        finally:
            submit.clean_temps()
        self.log(submit.name, break_cancel=True)

    def _drop_proc_info(self, pid):
        u''' 清除进程相关的信息。'''
        with self.redis.pipeline() as tx:
            tx.delete(f'{pid}:env')
            tx.delete(f'{pid}:args')
            tx.delete(pid)
            tx.execute()

    def _write_proc_info(self, pid, args, wd, env, auto_restart):
        u''' 将进程的基本信息写到redis '''
        with self.redis.pipeline() as tx:
            args_key = f'{pid}:args'
            env_key = f'{pid}:env'
            tx.delete(args_key, env_key, pid)

            tx.rpush(args_key, *args)
            if wd:
                tx.hset(pid, 'wd', wd)
            if env:
                tx.delete(env_key)
                for k, v in env.items():
                    tx.hset(env_key, k, v)
            if auto_restart:
                tx.hset(pid, 'auto_restart', auto_restart and '1' or '')
            tx.hset(pid, 'create_time', _now())
            tx.execute()

    def start_proc(self, vm, pid, args, wd=None, env=None, auto_restart=False):
        u''' 在指定的机器上启动进程。
        将启动信息写到redis，然后通知相关的代理启动进程。
        '''
        self._write_proc_info(pid, args, wd, env, auto_restart)
        # 将进程加到虚拟机中。
        self.redis.sadd(f'{vm}:procs', pid)
        return self.async_call(vm, 'start_proc', pid.encode())

    def kill_process(self, pid):
        u''' 停止某个进程。'''
        process = ProcessState.load(self.redis, pid)
        return self.kill_proc(process.agent, pid)

    def _make_worker_id(self, vm):
        return f"{'p'+vm[1:]}-worker"

    def start_worker(self, vm, num_cores=0, verbose=False):
        args = ["python.exe", "-mjindefund.dpool", "worker"]
        args += [f"--url={self.url}"]
        if num_cores:
            args += [f"--num_cores={num_cores}"]
        if verbose:
            args += ["-v"]
        pid = self._make_worker_id(vm)
        return self.start_proc(vm, pid, args, wd=self.work_dir, env={'PYTHONPATH': self.work_dir}, auto_restart=True)

    def stop_worker(self, vm):
        pid = self._make_worker_id(vm)
        return self.kill_proc(vm, pid)

    @property
    def _jupyter_agent(self):
        return f'a-{self.user}-{self.jupyter_ip}'

    @property
    def _jupyter_samples_server(self):
        return f'a-{self.user}-{self.startup_info.jupyter_samples_server}'

    def _config_jupyter(self):
        future = self.async_call(self._jupyter_agent, 'config_jupyter', None, timeout=0.5)
        try:
            prefix, payload = future.result()
            if prefix == 'ok':
                return payload.decode()
            if prefix == 'timeout':
                log.warning("启动Notebook失败，收到超时信号，代理可能未启动。")
        except Exception as ex:
            log.warning("config jupyter fail. %s", ex)

    def update_jupyter_samples(self, force=False):
        future = self.async_call(
            self._jupyter_samples_server, 'update_jupyter_samples', force and 'force'.encode() or None, timeout=3)
        try:
            prefix, payload = future.result()
            if prefix == 'ok':
                return payload.decode()
            if prefix == 'timeout':
                log.warning("update jupyter samples timeout.")
            if prefix == 'error':
                log.warning("update jupyter samples fail: %s", payload)
        except Exception as ex:
            log.warning("update jupyter samples fail. %s", ex)

    def start_jupyter(self):
        for _ in range(2):
            url = self._config_jupyter()
            if url:
                break
            log.warning('启动超时，重试一次。')

        config_file = os.path.join(self.work_dir, 'notebook_config.py')
        args = ["jupyter", "notebook", "--config", config_file]
        future = self.start_proc(self._jupyter_agent,
                                 self.jupyter_pid,
                                 args,
                                 wd=self.work_dir,
                                 env={'PYTHONPATH': self.work_dir},
                                 auto_restart=True)
        try:
            future.result()
            return url
        except: # pylint: disable=bare-except
            log.warning('启动Notebook失败，代理: %s.', self._jupyter_agent)
            return 'offline'

    @property
    def machines(self):
        u''' 显示集群当前的机器列表。
        '''
        machines = self.redis.smembers('::machines')
        if not machines:
            log.warning("当前集群中一台机器也木有，奇怪了。")
        return [machine.decode() for machine in machines]

    @property
    def agents(self):
        u''' 查看当前用户启动的用户代理进程。'''
        agents = self.redis.smembers(f'{self._uid}:agents')
        if not agents:
            log.debug("当前集群未给用户分配代理机器。")
        return [agent.decode() for agent in agents]

    @property
    def all_agents(self):
        u''' 返回当前所有机器的agents的id。'''
        machines = self.machines
        return [f'a-{self.user}-{remove_prefix(m, "m-")}' for m in machines]

    def init_user_agent(self, user, password):
        from jindefund.dpool.cipher import Cipher
        user = user or self.user
        password = Cipher(user).encrypt(password)
        payload = pickle.dumps(dict(user=user, password=password))
        machines = self.machines
        futures = []

        def on_done(machine, future):
            try:
                future.result()
            except Exception as ex:
                log.warning("启动用户代理于 %s 失败: %s", machine, ex)
            else:
                log.info("启动用户代理于 %s, ok.", machine)

        for machine in machines:
            log.info("开始安装并启动%s上的用户代理服务。", machine)
            future = self.async_call(machine, 'ua_setup', payload)
            future.add_done_callback(partial(on_done, machine))
            futures.append(future)

        concurrent.futures.wait(futures)

    def shutdown_user_agent(self):
        futures = []

        def on_done(machine, future):
            try:
                future.result()
            except Exception as ex:
                log.warning("关闭用户代理于 %s 失败: %s", machine, ex)
            else:
                log.info("关闭用户代理于 %s, ok.", machine)

        for machine in self.machines:
            future = self.async_call(machine, 'ua_shutdown',
                                     self.user.encode())
            future.add_done_callback(partial(on_done, machine))
            futures.append(future)
        concurrent.futures.wait(futures)

    def start_workers(self, agents=[]):
        if not agents:
            agents = self.all_agents

        futures = []

        def on_done(agent, f):
            try:
                f.result()
                log.info("启动工作进程(%s), ok.", agent)
            except Exception as ex:
                log.warning("启动工作进程(%s), 失败: %s.", agent, ex)

        for agent in agents:
            f = self.start_worker(agent)
            f.add_done_callback(partial(on_done, agent))
            futures.append(f)

        concurrent.futures.wait(futures)

    def _submit_script(self, name):
        u''' 为指定用户增加一个脚本任务。'''
        if not self.agents:
            return False, f"No resource to execute: {name}"

        user = self.user
        script_id = f"s-{user}-{name}"
        state = self.redis.hget(script_id, 'state')
        if state:
            state = state.decode()

        if state == TaskState.RUNNING:
            return False, f"Job is running: {name}"
        if state == TaskState.SUBMIT:
            return False, f"Duplicated Job: {name}"

        with self.redis.pipeline() as tx:
            tx.multi()
            tx.hset(script_id, 'name', name)
            tx.hset(script_id, 'user', user)
            tx.hset(script_id, 'submit_time', _now())
            tx.hset(script_id, 'state', TaskState.SUBMIT)
            # 删除作业列表
            tx.delete(f"{script_id}:jobs")
            tx.sadd(f"{self._uid}:scripts", script_id)
            tx.lpush(f"{self._uid}:submit_scripts", script_id)
            tx.lpush(f"{self._uid}:notify", "script-submit")
            tx.execute()
        return True, 'ok'

    def kill_proc(self, vm, pid):
        u''' 向某个进程发送结束信息 '''
        # 从proc列表中移除。
        self.redis.srem(f'{vm}:procs', pid)
        future = self.async_call(pid, 'kill', None)
        future.add_done_callback(lambda _: self._drop_proc_info(pid))
        return future

    def kill_script(self, name):
        u''' 停止某个作业。'''
        script = Script.from_name(self.redis, self.user, name)
        tasks = list(self._list_running_tasks(name))
        f = self.async_call(script.id, 'kill', timeout=3)

        def fn(f):
            if script.agent:
                self.redis.srem(f'{script.agent}:scripts', script.id)
            script.destroy()
            with self.redis.pipeline() as tx:
                self.redis.srem(f'u-{self.user}:scripts', script.id)
                self.redis.lrem(f'u-{self.user}:running_scripts', 0, script.id)
                self.redis.srem(f'u-{self.user}:finish_scripts', script.id)
                for task in tasks:
                    self.redis.srem(f'{task.worker}:running', task.id)
                    print('kill %s @ %s' % (task.id, task.worker))
                tx.execute()

        f.add_done_callback(fn)
        f.result()
        return f

    def _list_running_tasks(self, script_id=None):
        for pool in self._list_pools(script_id=script_id):
            pool = PoolState.load(self.redis, pool)
            for tid in pool.running_tasks:
                yield TaskObject.load(self.redis, tid)

    def list_running_tasks(self, script_id=None):
        u''' 列举所有正在执行的任务。'''
        tasks = list(self._list_running_tasks(script_id))
        return _make_dataframe(tasks, [
            'id', 'worker', 'state', 'elapse', 'label', 'script_id', 'call_depth', 'pid', 'create_time', 'start_time',
            'finish_time', 'timestamp', "mem_private", "cpu_percent", "num_children"
        ])

    def list_tasks(self, script_id):
        u''' 列举所有正在执行的任务。'''
        tasks = []
        for pool in self._list_pools(script_id=script_id):
            pool = PoolState.load(self.redis, pool)
            for tid in pool.get_tasks(self.redis):
                tasks.append(TaskObject.load(self.redis, tid))

        return _make_dataframe(tasks, [
            'id', 'worker', 'state', 'elapse', 'label', 'script_id', 'call_depth', 'pid', 'create_time', 'start_time',
            'finish_time', 'timestamp', "mem_private", "cpu_percent", "num_children"
        ])


    def schedule(self):
        u''' 显示等待队列 '''
        r = self.redis
        with r.pipeline() as tx:
            tx.multi()
            for user_submits in r.keys('u-*:submit_scripts'):
                tx.lrange(user_submits, 0, -1)
            v = tx.execute()

        with r.pipeline() as tx:
            tx.multi()
            for script in flatten(v):
                tx.hmget(script, 'submit_time', 'should_schedule_time', 'name', 'user')
            script_info = tx.execute()
            script_info = map(lambda t: tuple(map(lambda x: x and x.decode(), t)), script_info)
            scripts = [objectview({
                    'id': f's-{x[3]}-{x[2]}',
                    'name': x[2],
                    'owner': x[3],
                    'create_time': _from_timestamp(x[0]),
                    'should_schedule_time': _from_timestamp(x[1])
                }) for x in script_info]
            scripts = sorted(scripts, key=lambda x: x.create_time)

        return _make_dataframe(scripts, [
            'id', 'name', 'owner', 'create_time', 'should_schedule_time'
        ])
