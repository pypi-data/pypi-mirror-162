import example_demo.setting as setting
from example_demo.setting import setting_info
from example_demo.utils.exceptions import OnedatautilConfigException
import re
import os
import copy


def format_params(text: str, all_info: dict):
    if not text:
        return text
    key_params = re.findall('\{(.*?)\}', text)
    if key_params:
        for para in key_params:
            if all_info.get(para):
                text = text.replace('{%s}' % para, str(all_info.get(para)))
    return text


def get_sftp_ftp_source_info(setting_info, request_type):
    sftp_source = []
    file_download_all = setting_info.get("file_download_all")
    # source_get_connect_id = setting_info.get("source_get_connect_id")
    file_load_dir_from = setting_info.get("file_load_dir_from")
    file_target_download_path = setting_info.get("file_target_download_path")
    file_load_test_path = setting_info.get("file_load_test_path")

    file_load_dir_from = format_params(file_load_dir_from, setting_info)
    file_target_download_path = format_params(file_target_download_path, setting_info)
    file_load_test_path = format_params(file_load_test_path, setting_info)

    if not file_load_dir_from or not file_target_download_path or not file_download_all:
        raise OnedatautilConfigException('file download path  or file_target_download_path or file_load_dir_from no '
                                         'cfg!!')

    debug = setting_info.get("debug_enable")

    for file_index, file in enumerate(file_download_all):
        file_info = {}
        file = format_params(file, setting_info)
        local_filepath = os.path.join(file_target_download_path, file)
        if debug and file_load_test_path:
            local_filepath = os.path.join(file_load_test_path, file)
        file_info["request_type"] = request_type
        file_info["file_download"] = file
        file_info["remote_path"] = os.path.join(file_load_dir_from, file)
        file_info["local_filepath"] = local_filepath
        # file_info["conn_id"] = source_get_connect_id
        sftp_source.append(file_info)
    return sftp_source


def get_api_source_info(setting_info, request_type):
    # http 下载
    # 翻页的情况,页数不定,作为一次模板
    # 目前模板只支持单一url ,page 参数值变化的情况,所以理论上只会有一个数据源
    all_source = []
    source_info = {}
    url_format = setting_info.get("request_url_format")
    url_params = setting_info.get("request_url_params")
    source_info["url"] = url_format
    source_info["request_type"] = request_type
    # data_params = tuple()
    if url_params:
        for k, v in url_params.items():
            v = format_params(v, setting_info)
            url_params[k] = v
            # data_params += ((k, v),)
            # if v.startswith("{") and v.endswith("}"):
            #     v_para = v[1:-1]
            #     if setting_info.get(v_para):
            #         url_params[k] = setting_info.get(v_para)
        source_info["url_params"] = url_params

    for i, v in setting_info.items():
        if i.startswith("request"):
            source_info[i] = v

    return [source_info]


def get_mysql_soucre_info(setting_info, request_type):
    mysql_source = []
    mysql_sql_get = setting_info.get("mysql_sql_get")
    mysql_sql_get_param = setting_info.get("mysql_sql_get_param")
    all_sqls = []
    if not mysql_sql_get:
        raise OnedatautilConfigException('mysql download cfg not get sql')
    source_sql_all_param = re.findall('\{(.*?)\}', mysql_sql_get)
    all_sql_params = []
    if mysql_sql_get_param:
        sql_params = mysql_sql_get_param.split(";")
        for s_p in sql_params:
            one_kv = {}
            kvs = s_p.split(",")
            for kv in kvs:
                if not kv:
                    continue
                k, v = kv.split(":")
                one_kv[k] = v
            if one_kv:
                all_sql_params.append(one_kv)
    if source_sql_all_param:
        for base_param in source_sql_all_param:
            if setting_info.get(base_param):
                mysql_sql_get = mysql_sql_get.replace("{%s}" % base_param, str(setting_info.get(base_param)))
    for final_param in all_sql_params:
        c_source = copy.deepcopy(mysql_sql_get)
        for k, v in final_param.items():
            if "{%s}" % k in c_source:
                c_source = c_source.replace("{%s}" % k, str(v))
        all_sqls.append(c_source)
    if not all_sqls:
        all_sqls.append(mysql_sql_get)
    for sql in all_sqls:
        mysql_source_info = {}
        mysql_source_info["mysql_sql_get"] = sql
        mysql_source_info["request_type"] = request_type
        mysql_source.append(mysql_source_info)
        # source = copy.deepcopy()
    return mysql_source


def get_source_cfg(**kwargs):
    if kwargs:
        setting_info.update(kwargs)
    all_source = []
    request_type = setting.SOURCE_GET_REQUEST_TYPE
    if request_type in ('sftp', 'ftp'):
        all_source = get_sftp_ftp_source_info(setting_info, request_type)
    elif request_type == 'mysql':
        all_source = get_mysql_soucre_info(setting_info, request_type)
    elif request_type.startswith('api'):
        all_source = get_api_source_info(setting_info, request_type)
    return all_source
