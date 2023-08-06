# -*- coding: UTF-8 -*-
import traceback
import datetime
import time
import os
import zipfile
import pickle
import hashlib
import json
import pprint
import re
import shutil
import pandas as pd
from w3lib.url import canonicalize_url as _canonicalize_url


def check_path(path, min_size=0):
    """检查文件是否存在"""
    if not min_size:
        return True if os.path.exists(path) else False
    else:
        return True if os.path.exists(path) and os.path.getsize(path) >= min_size else False


def un_zip(file_name, out_path):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name)
    zip_file.extractall(out_path)
    zip_file.close()


def get_file_size(dir_path, date_str):
    count = 0
    for file in os.listdir(dir_path):
        if date_str in file:
            count += 1
    return count


def get_path_size(str_path):
    if not check_path(str_path):
        return 0

    if os.path.isfile(str_path):
        return os.path.getsize(str_path)

    n_total_size = 0
    for strRoot, lsDir, lsFiles in os.walk(str_path):
        # get child directory size
        for strDir in lsDir:
            n_total_size = n_total_size + get_path_size(os.path.join(strRoot, strDir))
        for strFile in lsFiles:
            n_total_size = n_total_size + os.path.getsize(os.path.join(strRoot, strFile))
    return n_total_size


def tuple_to_file(tuple_data, file_path):
    write_data_str = ','.join([str(x).strip() for x in tuple_data])
    with open(file_path, 'a') as file_object:
        file_object.write(write_data_str + '\n')
        file_object.close()


def get_next_check_time(hour=8, minute=30):
    """获取下一次交易日期"""
    hour = str(hour) if len(str(hour)) == 2 else '0' + str(hour)
    minute = str(minute) if len(str(minute)) == 2 else '0' + str(minute)

    cur_time = datetime.datetime.now()
    cur_week_day = cur_time.weekday()
    if cur_week_day == 4 or cur_week_day == 5:
        next_check_time_str = (cur_time + datetime.timedelta(days=3)).strftime("%Y-%m-%d") + 'T%s:%s:00' % (
            hour, minute)
    else:
        next_check_time_str = (cur_time + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + 'T%s:%s:00' % (
            hour, minute)
    return next_check_time_str


def get_current_date(date_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(date_format)


def get_now_timedate():
    return (datetime.datetime.today()).strftime('%Y%m%d%H')


def try_get(obj, path, default_value=''):
    try:
        for p in path:
            if obj is None:
                return default_value
            if isinstance(obj, list):
                obj = obj[p]
            else:
                obj = obj.get(p)
        return default_value if obj is None else obj
    except Exception as e:
        return default_value


def try_int(val_str, default_val=0):
    try:
        return int(val_str)
    except Exception as e:
        pass
    return default_val


def dumps_obj(obj):
    return pickle.dumps(obj)


def loads_obj(obj_str):
    return pickle.loads(obj_str)


def canonicalize_url(url):
    """
    url 归一化 会参数排序 及去掉锚点
    """
    return _canonicalize_url(url)


def get_md5(*args):
    """
    @summary: 获取唯一的32位md5
    ---------
    @param *args: 参与联合去重的值
    ---------
    @result: 7c8684bcbdfcea6697650aa53d7b1405
    """

    m = hashlib.md5()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def get_json(json_str):
    """
    @summary: 取json对象
    ---------
    @param json_str: json格式的字符串
    ---------
    @result: 返回json对象
    """

    try:
        return json.loads(json_str) if json_str else {}
    except Exception as e1:
        try:
            json_str = json_str.strip()
            json_str = json_str.replace("'", '"')
            keys = get_info(json_str, "(\w+):")
            for key in keys:
                json_str = json_str.replace(key, '"%s"' % key)

            return json.loads(json_str) if json_str else {}

        except Exception as e2:
            pass

        return {}


def dumps_json(data, indent=4, sort_keys=False):
    """
    @summary: 格式化json 用于打印
    ---------
    @param data: json格式的字符串或json对象
    ---------
    @result: 格式化后的字符串
    """
    try:
        if isinstance(data, str):
            data = get_json(data)

        data = json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            skipkeys=True,
            sort_keys=sort_keys,
            default=str,
        )

    except Exception as e:
        data = pprint.pformat(data)

    return data


_regexs = {}


def get_info(html, regexs, allow_repeat=True, fetch_one=False, split=None):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == "":
            continue

        if regex not in _regexs.keys():
            _regexs[regex] = re.compile(regex, re.S)

        if fetch_one:
            infos = _regexs[regex].search(html)
            if infos:
                infos = infos.groups()
            else:
                continue
        else:
            infos = _regexs[regex].findall(str(html))

        if len(infos) > 0:
            # print(regex)
            break

    if fetch_one:
        infos = infos if infos else ("",)
        return infos if len(infos) > 1 else infos[0]
    else:
        infos = allow_repeat and infos or sorted(set(infos), key=infos.index)
        infos = split.join(infos) if split else infos
        return infos


def get_date_list(date_str):
    date_list = []
    today_str = datetime.datetime.today().strftime('%Y%m%d')

    default_date_str = today_str
    if date_str == '':
        date_list.append(default_date_str)
    else:
        weekday_list = pd.bdate_range(date_str, default_date_str).date
        date_list = [x.strftime('%Y%m%d') for x in weekday_list]
    return date_list


def to_md5(t_str):
    hl = hashlib.md5()
    hl.update(t_str.encode(encoding='utf-8'))
    return hl.hexdigest()


def parse_url_join(base, url_params):
    url_params_str = ''
    for para_k, para_v in url_params.items():
        url_params_str += para_k + '=' + str(para_v) + '&'
    url = base + url_params_str[:-1]
    return url


def parse_list_files_join_path(ori_path, file_list, diff_os=False):
    return_file_list = []
    for file in file_list:
        fpath = os.path.join(ori_path, file) if not diff_os else ori_path + file
        return_file_list.append(fpath)
    return return_file_list
