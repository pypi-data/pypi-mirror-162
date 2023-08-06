import os
import datetime
import time
import traceback
import re
import sys
# from datetime import timedelta, datetime
from typing import TYPE_CHECKING, Callable, List, Optional, Union
import example_demo.commons.common_fun as common
from example_demo.commons.common_cfg import get_cfg_data
from example_demo.configuration import conf, initialize_config
from example_demo.exceptions import OnedatautilConfigException

project_name = conf.get("project", "name")

print(sys.path[0])


class BaseUrlSource(object):

    def init_setting_source(self):
        pass

    def parse_setting_url(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def close(self):
        pass


def format_list_vals(tar_val, tar_dict={}):
    tar_val = tar_val.split(";")
    for t_v in tar_val:
        if not t_v:
            continue
        try:
            tar_dict[t_v.split("=")[0]] = t_v.split("=")[1]
        except:
            print(f'format_list_vals may error {tar_val}')
            continue


# [project]
PROJECT_NAME = conf.get("project", "name")

# [debug]
DEBUG_ENABLE = conf.getboolean("debug", "enable")

# [source_get]
SOURCE_GET_CUSTOMIZE = conf.getboolean("source_get", "customize")

SOURCE_GET_REQUEST_TYPE = conf.get("source_get", "request_type")
SOURCE_GET_CONNECT_ID = conf.get("source_get", "connect_id")
SOURCE_GET_DATE = conf.get("source_get", "date")
SOURCE_GET_DATE_FORMAT = conf.get("source_get", "date_format")
if not SOURCE_GET_DATE_FORMAT:
    SOURCE_GET_DATE_FORMAT = '%Y-%m-%d'
# 默认时间前一天， ；支持 直接输入的 %Y-%m-%d 是否支持识别切换工作日和正常日期
# 时间，支持 直接输入的 %Y-%m-%d；workday 前一天工作日；day（默认） 前一天;
if not SOURCE_GET_DATE:
    SOURCE_GET_DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
        SOURCE_GET_DATE_FORMAT)
elif SOURCE_GET_DATE == 'now':
    SOURCE_GET_DATE = datetime.datetime.now().strftime(SOURCE_GET_DATE_FORMAT)
time_date = time.strptime(SOURCE_GET_DATE, SOURCE_GET_DATE_FORMAT)
SOURCE_GET_YEAR = time_date.tm_year

# 是否检查数据已存在
SOURCE_GET_CHECK = conf.getboolean("source_get", "check")

# dpool
DPOOL_ENABLE = conf.getboolean("dpool", "enable")
DPOOL_KEY = conf.get("dpool", "key")
DPOOL_JOBCTL_POOL = conf.get("dpool", "jobctl_pool")
DPOOL_LOAD_FROM_REDIS_ENABLE = conf.getboolean("dpool", "load_from_redis_enable")

# [邮件]
EMAIL_ENABLE = conf.getboolean("email", "enable")

EMAIL_HOST = conf.get("email", "host")
EMAIL_FROM = conf.get("email", "from")
EMAIL_USER_NAME = conf.get("email", "user_name")
email_to_list = conf.get("email", "to")
EMAIL_TO_LIST = []
if email_to_list:
    EMAIL_TO_LIST = [to_l for to_l in email_to_list.split(";") if to_l]

email_cc = conf.get("email", "cc")
EMAIL_CC = []
if email_cc:
    EMAIL_CC = [cc_l for cc_l in email_cc.split(";") if cc_l]

EMAIL_SUBJECT = conf.get("email", "subject")
EMAIL_CONTENT = conf.get("email", "content")
EMAIL_FILE_REPORT = conf.getboolean("email", "file_report", default_val=True)

# [dag]
DAG_ID = conf.get("dag", "id")
if not DAG_ID:
    DAG_ID = PROJECT_NAME
DAG_OWNER = conf.get("dag", "owner")
DAG_DESCRIPTION = conf.get("dag", "description")
DAG_TAG = []
dag_tag = conf.get("dag", "tag")
if dag_tag:
    DAG_TAG = [tag for tag in dag_tag.split(";") if tag]

DAG_SCHEDULE_INTERVAL = conf.get("dag", "schedule_interval")
DAG_CATCHUP = conf.getboolean("dag", "catchup")
DAG_START_DATE = datetime.date.today() - datetime.timedelta(days=1)

dag_start_date = conf.get("dag", "start_date")
if dag_start_date:
    try:
        DAG_START_DATE = time.strptime(dag_start_date, SOURCE_GET_DATE_FORMAT)
    except:
        pass

DAGRUN_TIMEOUT = datetime.timedelta(minutes=60)
dagrun_timeout = conf.get("dag", "dagrun_timeout")
time_args = {}
if dagrun_timeout:
    format_list_vals(dagrun_timeout, time_args)
if time_args:
    try:
        DAGRUN_TIMEOUT = datetime.timedelta(**time_args)
    except:
        DAGRUN_TIMEOUT = datetime.timedelta(minutes=60)

DAG_DEPENDS_ON_PAST = conf.getboolean("dag", "depends_on_past")

DAG_EMAIL = []
dag_email = conf.get("dag", "email_receivers")
if dag_email:
    DAG_EMAIL = [e_l for e_l in dag_email.split(";") if e_l]

if not DAG_EMAIL and EMAIL_TO_LIST:
    DAG_EMAIL = EMAIL_TO_LIST

DAG_EMAIL_ON_FAILURE = conf.getboolean("dag", "email_on_failure", default_val=True)
DAG_EMAIL_ON_RETRY = conf.getboolean("dag", "email_on_retry")
DAG_RETRIES = conf.getint("dag", "retries", default_int=1)
# 重试间隔
DAGRUN_TIMEOUT = datetime.timedelta(seconds=60)
dag_retry_delay = conf.get("dag", "retry_delay")
dag_retry_delay_time_args = {}
if dag_retry_delay:
    format_list_vals(dag_retry_delay, dag_retry_delay_time_args)
if dag_retry_delay_time_args:
    try:
        DAG_RETRY_DELAY = datetime.timedelta(**dag_retry_delay_time_args)
    except:
        pass

# [pipeline]
PIPELINE_FR_ENABLE = conf.getboolean("pipeline", "fr_enable")
PIPELINE_REDIS_SERVER_IP = conf.get("pipeline", "redis_server_ip")
PIPELINE_REDIS_SERVER_PORT = conf.get("pipeline", "redis_server_port")
PIPELINE_PROXY_IP = conf.get("pipeline", "proxy_ip")
PIPELINE_DOMAIN_NAME = conf.get("pipeline", "domain_name")
PIPELINR_CHECK_KEY = conf.get("pipeline", "check_key")
PIPELINE_PROJECT_NAME = conf.get("pipeline", "project_name")
# 是否上报失败文件信息，默认关闭
PIPELINE_FR_FAIL = conf.getboolean("pipeline", "fr_fail")

# [tel]
TEL_ENABLE = conf.getboolean("tel", "enable")
TEL_CONTACTS = conf.get("tel", "contacts")
if TEL_CONTACTS:
    TEL_CONTACTS = TEL_CONTACTS.split(";")
TEL_OPTNAME = conf.get("tel", "optname")

TEL_SUB_DATE_TYOE = conf.get("tel", "sub_data_type")
# TEL_SUB_DATE_TYPE = ''
# TEL_REMIND_INFO = ''
# TEL_TEMPLATE_NO = ''
# TEL_STATUS = ''
# TEL_CALLTIMES = ''
# TEL_MEMO = ''


# [mssqldb]
#  r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
MSSQLDB_ENABLE = conf.getboolean("mssql", "enable")
MSSQLDB_CONNECT_URL = conf.get("mssql", "connect_url")
MSSQLDB_TABLE = conf.get("mssql", "table")
# SQLDB_CHECK_SQL

# [mysql]
MYSQL_ENABLE = conf.getboolean("mysql", "enable")
MYSQL_HOST = conf.get("mysql", "host")
MYSQL_PORT = conf.getint("mysql", "port", default_int=3306)
MYSQL_USER = conf.get("mysql", "user")
MYSQL_PASSWORD = conf.get("mysql", "password")
MYSQL_DB_NAME = conf.get("mysql", "db")

MYSQL_SQL_GET = conf.get("mysql", "sql_get")
MYSQL_SQL_PARAM = conf.get("mysql", "sql_get_param")
# eg : sql = select alertid,subject,sendto,clock from alerts where subject
# like '%{subject_like}%' and (sendto like '%{receiver_like}%') order by clock desc limit 0,1
SOURCE_SQL = conf.get("mysql", "source_get_sql")
SOURCE_SQL_PARAM = conf.get("mysql", "source_get_sql_param")

# [redis]
REDIS_ENABLE = conf.getboolean("redis", "enable")
REDIS_HOST = conf.get("redis", "host")
REDIS_PORT = conf.get("redis", "port")
REDIS_PASSWORD = conf.get("redis", "password")
REDIS_LOAD_DB = conf.get("redis", "load_db")
REDIS_PROXY_DB = conf.get("redis", "proxy_db")
#
# REDIS_SLAVER = ''
# REDIS_VALUE0 = ''
# REDIS_VALUE1 = ''

# [ldb]
LDB_ENABLE = conf.getboolean("ldb", "enable")
#  r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
LDB_TARGET = conf.getboolean("ldb", "target")
#
LDB_SCHEMA = conf.getboolean("ldb", "schema")

# [clean]
CLEAN_WARNING = ''
CLEAN_ERROR = ''

# may depre
# [source]
SOURCE_CHECK_OUT_DATA = 0
SOURCE_DATE = ''
SOURCE_DATE_FORMAT = ''
SOURCE_YEAR = ''
#
SOURCE_REQUEST_TIMEOUT = 10
SOURCE_REQUEST_TRYNUM = 3
# reqest请求下载文件路径，通常场景是request请求后，下载转存为文件。默认为空即不需要下载转存，有值时为下载路径，支持直接路径全称也支持格式化{}，比如{source_file_target_download_fpath}
# 这里是有可能会有多个的，另外可能和本地缓存功能一致？
SOURCE_REQUEST_LOAD_FILE_PATH = ''

FILE_ENABLE = conf.getboolean("file", "enable")
SOURCE_DOWNLOAD_FILES = ''
SOURCE_FILE_TARGET_DOWNLOAD_PATH = ''
SOURCE_FILE_TARGET_DOWNLOAD_FPATH = ''
SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH = ''
SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH = ''
SOURCE_FILE_UNZIP_OUT_PATH = ''
SOURCE_LOAD_DIR_FROM = ''
SOURCE_LOAD_FILE_FROM = []
# 对缓存文件的处理，会将缓存文件转存入 SOURCE_FILE_TARGET_DOWNLOAD_PATH，默认关闭
SOURCE_FILE_CACHE_COPY_ENABLE = False
# 对缓存文件的处理，会在程序结束时将缓存文件删除，默认关闭
SOURCE_FILE_CACHE_DEL_ENABLE = False
SOURCE_LOCAL_LOAD_DIR_CACHE = ''
SOURCE_FILE_LOAD_TEST_PATH = ''
SOURCE_LOAD_FILE_MINSIZE = 0

# api
SOURCE_URL_FORMAT = ''
SOURCE_URL_PARAMS = {}
SOURCE_URL_START_PAGE = ''
SOURCE_URL_STOP_PAGE_NUM = ''
SOURCE_URL_PAGESIZE = ''

SOURCE_NEED_UA = False
SOURCE_DEFAULT_UA = ''
SOURCE_REQUEST_AUTH_NAME = ''
SOURCE_REQUEST_AUTH_PASSWORD = ''

# sftp
SFTP_HOST = conf.get("sftp", "host")
SFTP_PORT = conf.getint("sftp", "port")
SFTP_USER = conf.get("sftp", "user")
SFTP_PASSWORD = conf.get("sftp", "password")
if SFTP_USER and SFTP_PASSWORD:
    SFTP_USER = SFTP_USER.split(";")
    SFTP_PASSWORD = SFTP_PASSWORD.split(";")
SFTP_USER_INDEX = conf.get("sftp", "user_index")

# ftp
FTP_IP = conf.get("ftp", "ip")
FTP_PORT = conf.getint("ftp", "port")
FTP_USER_ID = conf.get("ftp", "user_id")
FTP_USER_PASSWORD = conf.get("ftp", "user_password")

# 保留待废弃
SOURCE_FTP_IP = ''
SOURCE_FTP_PORT = ''

SOURCE_FTP_USER_ID = ''
SOURCE_FTP_USER_PASSWORD = ''

SOURCE_FTP_TARGET_DIR_DOWNLOAD = ''
SOURCE_FTP_REAL_TARGET_DIR_DOWNLOAD = ''

# db
SOURCE_SQL = ''
SOURCE_SQL_PARAM = ''

# [parser]
# PARSER_DATE = ''
# PARSER_DATE_FORMAT = ''

# may deprecated
program_config = {}
CONFIG_FILE = "project.cfg"
cfg_path = (os.path.join(os.getcwd(), CONFIG_FILE))
if common.check_path(cfg_path):
    program_config = get_cfg_data(cfg_path, need_dict=True)
setting_info = {}


def format_params(text: str, all_info: dict):
    key_params = re.findall('\{(.*?)\}', text)
    if key_params:
        for para in key_params:
            if all_info.get(para):
                text = text.replace('{%s}' % para, str(all_info.get(para)))
    return text


def init_program_base():
    global PROJECT_NAME
    global DEBUG_ENABLE

    global SOURCE_GET_REQUEST_TYPE
    global SOURCE_GET_CUSTOMIZE

    global SOURCE_GET_CHECK
    # [project]
    PROJECT_NAME = conf.get("project", "name")

    # [debug]
    DEBUG_ENABLE = conf.getboolean("debug", "enable")

    SOURCE_GET_CUSTOMIZE = conf.getboolean("source_get", "customize")

    SOURCE_GET_REQUEST_TYPE = conf.get("source_get", "request_type")

    # 是否检查数据已存在
    SOURCE_GET_CHECK = conf.getboolean("source_get", "check")
    # SOURCE_GET_CONNECT_ID = conf.get("source_get", "connect_id")

    SOURCE_GET_DATE = conf.get("source_get", "date")
    SOURCE_GET_DATE_FORMAT = conf.get("source_get", "date_format")
    if not SOURCE_GET_DATE_FORMAT:
        SOURCE_GET_DATE_FORMAT = '%Y-%m-%d'
    # 默认时间前一天， ；支持 直接输入的 %Y-%m-%d 是否支持识别切换工作日和正常日期
    # 时间，支持 直接输入的 %Y-%m-%d；workday 前一天工作日；day（默认） 前一天;
    if not SOURCE_GET_DATE:
        SOURCE_GET_DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
            SOURCE_GET_DATE_FORMAT)
    elif SOURCE_GET_DATE == 'now':
        SOURCE_GET_DATE = datetime.datetime.now().strftime(SOURCE_GET_DATE_FORMAT)
    time_date = time.strptime(SOURCE_GET_DATE, SOURCE_GET_DATE_FORMAT)
    SOURCE_GET_YEAR = time_date.tm_year


class SettingInit():
    def __init__(self, setting_info):
        self.setting_info = setting_info

    def init_airflow_dag_info(self):
        '''初始化dag 配置信息'''

        default_args = {
            'owner': DAG_OWNER,  # 拥有者名称
            'depends_on_past': DAG_DEPENDS_ON_PAST,  # 是否依赖于过去。如果为True，那么必须要前次的DAG执行成功了，此次的DAG才能执行。
            'start_date': DAG_START_DATE,  #
            'email': DAG_EMAIL,  # 出问题时，发送报警Email的地址，可以填多个，用逗号隔开。
            'email_on_failure': DAG_EMAIL_ON_FAILURE,  # 任务失败且重试次数用完时是否发送Email。
            'email_on_retry': DAG_EMAIL_ON_RETRY,  # 任务重试时是否发送Email
            'retries': DAG_RETRIES,  # 失败重试次数
            'retry_delay': DAGRUN_TIMEOUT,  # 失败重试间隔
        }
        # access_control = {
        #     'JD_DATAOPS': {'can_edit', 'can_delete', 'can_read'},
        #     'zhangyf': {'can_edit', 'can_delete', 'can_read'}
        # }

        if not DAG_SCHEDULE_INTERVAL:
            print('no dag schedule_interval cfg!!')
            raise OnedatautilConfigException(f"dag schedule_interval  not found in config")

        DAG_ARGS = dict(
            dag_id=DAG_ID,
            default_args=default_args,
            description=DAG_DESCRIPTION,
            schedule_interval=DAG_SCHEDULE_INTERVAL,  # 调度时间规则同crontab，注意下默认是utc时间，与当前时间差了8小时，实际为8点0分启动
            dagrun_timeout=DAGRUN_TIMEOUT,
            catchup=DAG_CATCHUP,
            dag_tag=DAG_TAG,
            # access_control=access_control
        )
        return DAG_ARGS

    def init_sftp_info(self):
        global SFTP_HOST
        global SFTP_PORT
        global SFTP_USER
        global SFTP_PASSWORD
        global SFTP_USER_INDEX
        SFTP_HOST = conf.get("sftp", "host")
        SFTP_PORT = conf.getint("sftp", "port")
        SFTP_USER = conf.get("sftp", "user")
        SFTP_PASSWORD = conf.get("sftp", "password")
        if SFTP_USER and SFTP_PASSWORD:
            SFTP_USER = SFTP_USER.split(";")
            SFTP_PASSWORD = SFTP_PASSWORD.split(";")
        SFTP_USER_INDEX = conf.get("sftp", "user_index")

        self.setting_info["sftp_host"] = SFTP_HOST
        self.setting_info["sftp_port"] = SFTP_PORT
        self.setting_info["sftp_user"] = SFTP_USER
        self.setting_info["sftp_password"] = SFTP_PASSWORD
        self.setting_info["sftp_user_index"] = SFTP_PASSWORD

    def init_ftp_info(self):
        global SOURCE_FTP_IP
        global SOURCE_FTP_PORT
        global SOURCE_FTP_USER_ID
        global SOURCE_FTP_USER_PASSWORD

        SOURCE_FTP_IP = conf.get("ftp", "ip") or common.try_get(program_config, ["source", "ftp_ip"])
        SOURCE_FTP_PORT = conf.getint("ftp", "port") or common.try_int(
            common.try_get(program_config, ["source", "ftp_port"]))

        SOURCE_FTP_USER_ID = conf.get("ftp", "user_id") or common.try_get(program_config, ["source", "ftp_user_id"])
        SOURCE_FTP_USER_PASSWORD = conf.get("ftp", "user_password") or common.try_get(program_config,
                                                                                      ["source", "ftp_user_password"])
        if SOURCE_FTP_IP:
            self.setting_info['ftp_ip'] = SOURCE_FTP_IP,
            self.setting_info['ftp_port'] = SOURCE_FTP_PORT,
            self.setting_info['ftp_user_id'] = SOURCE_FTP_USER_ID,
            self.setting_info['ftp_user_password'] = SOURCE_FTP_USER_PASSWORD,

    def init_request_info(self):
        global SOURCE_URL_FORMAT
        global SOURCE_URL_PARAMS
        global SOURCE_REQUEST_LOAD_FILE_PATH
        global SOURCE_REQUEST_TIMEOUT
        global SOURCE_REQUEST_TRYNUM
        global SOURCE_NEED_UA
        global SOURCE_DEFAULT_UA
        global SOURCE_REQUEST_AUTH_NAME
        global SOURCE_REQUEST_AUTH_PASSWORD
        global SOURCE_URL_START_PAGE
        global SOURCE_URL_STOP_PAGE_NUM
        global SOURCE_URL_PAGESIZE

        SOURCE_URL_FORMAT = conf.get("request", "url_format") or common.try_get(program_config,
                                                                                ["source", "url_format"])
        url_params = conf.get("request", "url_params") or common.try_get(program_config, ["source", "url_params"])
        if url_params:
            url_params = url_params.split(';')
            for para in url_params:
                if not para:
                    continue
                para_ = para.split('->')
                if len(para_) == 2:
                    SOURCE_URL_PARAMS[para_[0]] = para_[1]
                elif len(para_) == 1:
                    SOURCE_URL_PARAMS[para_[0]] = ''
                else:
                    continue
        SOURCE_URL_START_PAGE = conf.getint(
            "request", "url_start_page", default_int=1) or common.try_int(
            common.try_get(program_config, ["source", "url_start_page"]))
        SOURCE_URL_STOP_PAGE_NUM = conf.getint("request", "url_stop_page_num", default_int=0) or common.try_int(
            common.try_get(program_config, ["source", "url_stop_page_num"]))
        SOURCE_URL_PAGESIZE = conf.getint("request", "url_pagesize") or common.try_int(
            common.try_get(program_config, ["source", "url_pagesize"]))
        SOURCE_REQUEST_TIMEOUT = conf.get("request", "timeout") or common.try_int(
            common.try_get(program_config, ["source", "request_timeout"]))
        SOURCE_REQUEST_TRYNUM = conf.getint("request", "trynum", default_int=3) or common.try_int(
            common.try_get(program_config, ["source", "request_trynum"]))

        SOURCE_NEED_UA = conf.getboolean("request", "need_ua") or common.try_get(program_config, ["source", "need_ua"])
        # may deprecated
        SOURCE_DEFAULT_UA = conf.get("request", "default_ua") or common.try_get(program_config,
                                                                                ["source", "default_ua"])

        SOURCE_REQUEST_AUTH_NAME = conf.get("request", "auth_name") or common.try_get(program_config,
                                                                                      ["source", "request_auth_name"])
        SOURCE_REQUEST_AUTH_PASSWORD = conf.get("request", "auth_password") or common.try_get(program_config, ["source",
                                                                                                               "request_auth_password"])

        SOURCE_REQUEST_LOAD_FILE_PATH = conf.get("request", "load_file_path") or common.try_get(program_config,
                                                                                                ["source",
                                                                                                 "request_load_file_path"])

        self.setting_info['request_url_format'] = SOURCE_URL_FORMAT
        self.setting_info['request_url_params'] = SOURCE_URL_PARAMS
        self.setting_info['request_timeout'] = SOURCE_REQUEST_TIMEOUT
        self.setting_info['request_trynum'] = SOURCE_REQUEST_TRYNUM
        self.setting_info['request_url_start_page'] = SOURCE_URL_START_PAGE
        self.setting_info['request_url_stop_page'] = SOURCE_URL_STOP_PAGE_NUM
        self.setting_info['request_url_pagesize'] = SOURCE_URL_PAGESIZE
        self.setting_info['request_timeout'] = SOURCE_REQUEST_TIMEOUT
        self.setting_info['request_trynum'] = SOURCE_REQUEST_TRYNUM
        self.setting_info['request_need_ua'] = SOURCE_NEED_UA
        # self.setting_info['request_default_ua'] = SOURCE_DEFAULT_UA
        self.setting_info['request_auth_name'] = SOURCE_REQUEST_AUTH_NAME
        self.setting_info['request_auth_password'] = SOURCE_REQUEST_AUTH_PASSWORD
        self.setting_info['request_load_file_path'] = SOURCE_REQUEST_LOAD_FILE_PATH

    def init_mysql_info(self):
        global MYSQL_ENABLE
        global MYSQL_HOST
        global MYSQL_PORT
        global MYSQL_PASSWORD
        global MYSQL_USER
        global MYSQL_DB_NAME
        global MYSQL_SQL_GET
        global MYSQL_SQL_PARAM
        global SOURCE_SQL
        global SOURCE_SQL_PARAM
        MYSQL_ENABLE = conf.getboolean("mysql", "enable")
        MYSQL_HOST = conf.get("mysql", "host")
        MYSQL_PORT = conf.getint("mysql", "port", default_int=3306)
        MYSQL_USER = conf.get("mysql", "user")
        MYSQL_PASSWORD = conf.get("mysql", "password")
        MYSQL_DB_NAME = conf.get("mysql", "db")

        MYSQL_SQL_GET = conf.get("mysql", "sql_get")
        MYSQL_SQL_PARAM = conf.get("mysql", "sql_get_param")
        # eg : sql = select alertid,subject,sendto,clock from alerts where subject
        # like '%{subject_like}%' and (sendto like '%{receiver_like}%') order by clock desc limit 0,1
        SOURCE_SQL = conf.get("mysql", "source_get_sql")
        SOURCE_SQL_PARAM = conf.get("mysql", "source_get_sql_param")
        if MYSQL_ENABLE:
            self.setting_info["mysql_enable"] = MYSQL_ENABLE
            self.setting_info["mysql_host"] = MYSQL_HOST
            self.setting_info["mysql_port"] = MYSQL_PORT
            self.setting_info["mysql_user"] = MYSQL_USER
            self.setting_info["mysql_password"] = MYSQL_PASSWORD
            self.setting_info["mysql_db_name"] = MYSQL_DB_NAME
            self.setting_info["mysql_sql_get"] = MYSQL_SQL_GET
            self.setting_info["mysql_sql_get_param"] = MYSQL_SQL_PARAM
            self.setting_info["source_sql"] = SOURCE_SQL
            self.setting_info["source_sql_param"] = SOURCE_SQL_PARAM

    def init_mssql_info(self):
        global MSSQLDB_ENABLE
        global MSSQLDB_CONNECT_URL
        global MSSQLDB_TABLE

        MSSQLDB_ENABLE = conf.getboolean("mssql", "enable")
        MSSQLDB_CONNECT_URL = conf.get("mssql", "connect_url")
        MSSQLDB_TABLE = conf.get("mssql", "table")
        if MSSQLDB_ENABLE:
            self.setting_info["mssqldb_enable"] = MSSQLDB_ENABLE
            self.setting_info["mssqldb_connect_url"] = MSSQLDB_CONNECT_URL
            self.setting_info["mssqldb_table"] = MSSQLDB_TABLE

    def init_redis_info(self):
        global REDIS_ENABLE
        global REDIS_HOST
        global REDIS_PORT
        global REDIS_PASSWORD
        global REDIS_LOAD_DB
        global REDIS_PROXY_DB

        REDIS_ENABLE = conf.getboolean("redis", "enable")
        REDIS_HOST = conf.get("redis", "host")
        REDIS_PORT = conf.get("redis", "port")
        REDIS_PASSWORD = conf.get("redis", "password")
        REDIS_LOAD_DB = conf.get("redis", "load_db")
        REDIS_PROXY_DB = conf.get("redis", "proxy_db")
        if REDIS_ENABLE:
            self.setting_info["redis_enable"] = REDIS_ENABLE
            self.setting_info["redis_host"] = REDIS_HOST
            self.setting_info["redis_port"] = REDIS_PORT
            self.setting_info["redis_password"] = REDIS_PASSWORD
            self.setting_info["redis_load_db"] = REDIS_LOAD_DB
            self.setting_info["redis_proxy_db"] = REDIS_PROXY_DB

    def init_file_info(self):
        global FILE_ENABLE
        global SOURCE_DOWNLOAD_FILES
        global SOURCE_FILE_TARGET_DOWNLOAD_PATH
        global SOURCE_FILE_TARGET_DOWNLOAD_FPATH
        global SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH
        global SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH
        global SOURCE_FILE_UNZIP_OUT_PATH
        global SOURCE_LOAD_DIR_FROM
        global SOURCE_LOAD_FILE_FROM
        global SOURCE_LOCAL_LOAD_DIR_CACHE
        global SOURCE_FILE_CACHE_DEL_ENABLE
        global SOURCE_FILE_CACHE_COPY_ENABLE
        global SOURCE_FILE_LOAD_TEST_PATH
        global SOURCE_LOAD_FILE_MINSIZE

        FILE_ENABLE = conf.getboolean("file", "enable")

        SOURCE_DOWNLOAD_FILES = conf.get("file", "download_all") or common.try_get(program_config,
                                                                                   ["source", "download_files"])
        if SOURCE_DOWNLOAD_FILES:
            SOURCE_DOWNLOAD_FILES = SOURCE_DOWNLOAD_FILES.split(";")
            SOURCE_DOWNLOAD_FILES = [file for file in SOURCE_DOWNLOAD_FILES if file]
        SOURCE_FILE_TARGET_DOWNLOAD_PATH = common.try_get(program_config,
                                                          ["source", "file_target_download_path"]) or conf.get("file",
                                                                                                               "target_download_path")
        SOURCE_FILE_TARGET_DOWNLOAD_FPATH = common.try_get(program_config,
                                                           ["source", "file_target_download_fpath"]) or conf.get("file",
                                                                                                                 "target_download_fpath")
        if SOURCE_DOWNLOAD_FILES and SOURCE_FILE_TARGET_DOWNLOAD_PATH and not SOURCE_FILE_TARGET_DOWNLOAD_FPATH:
            SOURCE_FILE_TARGET_DOWNLOAD_FPATH = common.parse_list_files_join_path(SOURCE_FILE_TARGET_DOWNLOAD_PATH,
                                                                                  SOURCE_DOWNLOAD_FILES)

        SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH = common.try_get(program_config,
                                                               ["source",
                                                                "real_file_target_download_path"]) or conf.get(
            "file", "real_target_download_path")
        SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH = common.try_get(program_config,
                                                                ["source",
                                                                 "real_file_target_download_fpath"]) or conf.get(
            "file", "real_target_download_fpath")
        if SOURCE_DOWNLOAD_FILES and SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH and not SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH:
            SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH = common.parse_list_files_join_path(
                SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH,
                SOURCE_DOWNLOAD_FILES, diff_os=True)
        SOURCE_FILE_UNZIP_OUT_PATH = conf.get(
            "file", "unzip_out_path") or common.try_get(program_config, ["source", "file_unzip_out_path"])
        SOURCE_LOAD_DIR_FROM = conf.get("file", "load_dir_from") or common.try_get(program_config,
                                                                                   ["source", "load_dir_from"])
        source_load_file_from = conf.get("file", "load_file_from") or common.try_get(program_config,
                                                                                     ["source", "load_file_from"])
        if SOURCE_DOWNLOAD_FILES and SOURCE_LOAD_DIR_FROM and not source_load_file_from:
            SOURCE_LOAD_FILE_FROM = common.parse_list_files_join_path(SOURCE_LOAD_DIR_FROM, SOURCE_DOWNLOAD_FILES)

        SOURCE_LOCAL_LOAD_DIR_CACHE = common.try_get(program_config, ["source", "local_load_dir_cache"]) or conf.get(
            "file", "local_load_dir_cache")
        source_file_cache_copy_enable = common.try_get(program_config, ["source", "file_cache_copy_enable"])
        if source_file_cache_copy_enable == 'True' or conf.getboolean("file", "cache_copy_enable"):
            SOURCE_FILE_CACHE_COPY_ENABLE = True
        source_file_cache_del_enable = common.try_get(program_config, ["source", "file_cache_del_enable"])
        if source_file_cache_del_enable == 'True' or conf.getboolean("file", "cache_del_enable"):
            SOURCE_FILE_CACHE_DEL_ENABLE = True

        SOURCE_FILE_LOAD_TEST_PATH = conf.get(
            "file", "load_test_path") or common.try_get(program_config, ["source", "file_load_test_path"])
        SOURCE_LOAD_FILE_MINSIZE = conf.getint("file", "load_minsize", default_int=0) or common.try_int(
            common.try_get(program_config, ["source", "load_file_minsize"], default_value=0))
        if FILE_ENABLE:
            self.setting_info["file_enable"] = FILE_ENABLE
            self.setting_info["file_download_all"] = SOURCE_DOWNLOAD_FILES
            self.setting_info["file_target_download_path"] = SOURCE_FILE_TARGET_DOWNLOAD_PATH
            self.setting_info["file_target_download_fpath"] = SOURCE_FILE_TARGET_DOWNLOAD_FPATH
            self.setting_info["file_real_target_download_path"] = SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH
            self.setting_info["file_real_target_download_fpath"] = SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH

            self.setting_info["file_unzip_out_path"] = SOURCE_FILE_UNZIP_OUT_PATH
            self.setting_info["file_load_dir_from"] = SOURCE_LOAD_DIR_FROM
            self.setting_info["file_load_file_from"] = SOURCE_LOAD_FILE_FROM
            self.setting_info["file_local_load_dir_cache"] = SOURCE_LOCAL_LOAD_DIR_CACHE
            self.setting_info["file_cache_copy_enable"] = SOURCE_FILE_CACHE_COPY_ENABLE
            self.setting_info["file_cache_del_enable"] = SOURCE_FILE_CACHE_DEL_ENABLE
            self.setting_info["file_load_test_path"] = SOURCE_FILE_LOAD_TEST_PATH
            self.setting_info["file_load_minsize"] = SOURCE_LOAD_FILE_MINSIZE

    def init_email_info(self):
        global EMAIL_ENABLE
        global EMAIL_HOST
        global EMAIL_FROM
        global EMAIL_CC
        global EMAIL_USER_NAME
        global EMAIL_TO_LIST
        global EMAIL_SUBJECT
        global EMAIL_CONTENT
        global EMAIL_FILE_REPORT

        EMAIL_ENABLE = conf.getboolean("email", "enable")

        EMAIL_HOST = conf.get("email", "host")
        EMAIL_FROM = conf.get("email", "from")
        EMAIL_USER_NAME = conf.get("email", "user_name")
        email_to_list = conf.get("email", "to")
        EMAIL_TO_LIST = []
        if email_to_list:
            EMAIL_TO_LIST = [to_l for to_l in email_to_list.split(";") if to_l]

        email_cc = conf.get("email", "cc")
        EMAIL_CC = []
        if email_cc:
            EMAIL_CC = [cc_l for cc_l in email_cc.split(";") if cc_l]

        EMAIL_SUBJECT = conf.get("email", "subject")
        EMAIL_CONTENT = conf.get("email", "content")
        EMAIL_FILE_REPORT = conf.getboolean("email", "file_report", default_val=True)

        self.setting_info["email_enable"] = EMAIL_ENABLE
        self.setting_info["email_host"] = EMAIL_HOST
        self.setting_info["email_from"] = EMAIL_FROM
        self.setting_info["email_user_name"] = EMAIL_USER_NAME
        self.setting_info["email_subject"] = EMAIL_SUBJECT
        self.setting_info["email_content"] = EMAIL_CONTENT
        self.setting_info["email_cc"] = EMAIL_CC
        self.setting_info["email_to_list"] = EMAIL_TO_LIST
        self.setting_info["email_file_report"] = EMAIL_FILE_REPORT

    def init_pipeline_info(self):
        global PIPELINE_FR_ENABLE
        global PIPELINE_FR_FAIL
        global PIPELINE_PROJECT_NAME
        global PIPELINE_PROXY_IP
        global PIPELINR_CHECK_KEY
        global PIPELINE_REDIS_SERVER_IP
        global PIPELINE_REDIS_SERVER_PORT
        global PIPELINE_DOMAIN_NAME
        PIPELINE_FR_ENABLE = conf.getboolean("pipeline", "fr_enable")
        PIPELINE_REDIS_SERVER_IP = conf.get("pipeline", "redis_server_ip")
        PIPELINE_REDIS_SERVER_PORT = conf.get("pipeline", "redis_server_port")
        PIPELINE_PROXY_IP = conf.get("pipeline", "proxy_ip")
        PIPELINE_DOMAIN_NAME = conf.get("pipeline", "domain_name")
        PIPELINR_CHECK_KEY = conf.get("pipeline", "check_key")
        PIPELINE_PROJECT_NAME = conf.get("pipeline", "project_name")
        # 是否上报失败文件信息，默认关闭
        PIPELINE_FR_FAIL = conf.getboolean("pipeline", "fr_fail")
        if PIPELINE_FR_ENABLE:
            self.setting_info["pipeline_fr_enable"] = PIPELINE_FR_ENABLE
            self.setting_info["pipeline_redis_server_ip"] = PIPELINE_REDIS_SERVER_IP
            self.setting_info["pipeline_redis_server_port"] = PIPELINE_REDIS_SERVER_PORT
            self.setting_info["pipeline_proxy_ip"] = PIPELINE_PROXY_IP
            self.setting_info["pipeline_domain_name"] = PIPELINE_DOMAIN_NAME
            self.setting_info["pipeline_check_key"] = PIPELINR_CHECK_KEY
            self.setting_info["pipeline_project_name"] = PIPELINE_PROJECT_NAME
            self.setting_info["pipeline_fr_fail"] = PIPELINE_FR_FAIL

    def init_tel_info(self):

        global TEL_ENABLE
        global TEL_CONTACTS
        global TEL_OPTNAME
        global TEL_SUB_DATE_TYOE
        global TEL_SUB_DATE_TYOE
        TEL_ENABLE = conf.getboolean("tel", "enable")
        TEL_CONTACTS = conf.get("tel", "contacts")
        if TEL_CONTACTS:
            TEL_CONTACTS = TEL_CONTACTS.split(";")
        TEL_OPTNAME = conf.get("tel", "optname")

        TEL_SUB_DATE_TYOE = conf.get("tel", "sub_data_type")
        if TEL_ENABLE:
            self.setting_info["tel_enable"] = TEL_ENABLE
            self.setting_info["tel_contacts"] = TEL_CONTACTS
            self.setting_info["tel_optname"] = TEL_OPTNAME

    def init_dpool_info(self):
        global DPOOL_ENABLE
        global DPOOL_JOBCTL_POOL
        global DPOOL_KEY
        global DPOOL_LOAD_FROM_REDIS_ENABLE
        DPOOL_ENABLE = conf.getboolean("dpool", "enable")
        DPOOL_KEY = conf.get("dpool", "key")
        DPOOL_JOBCTL_POOL = conf.get("dpool", "jobctl_pool")
        DPOOL_LOAD_FROM_REDIS_ENABLE = conf.getboolean("dpool", "load_from_redis_enable")
        if DPOOL_ENABLE:
            self.setting_info["dpool_enable"] = DPOOL_ENABLE
            self.setting_info["dpool_key"] = DPOOL_KEY
            self.setting_info["dpool_jobctl_pool"] = DPOOL_JOBCTL_POOL
            self.setting_info["dpool_load_from_redis_enable"] = DPOOL_LOAD_FROM_REDIS_ENABLE

    def init_parser_info(self):
        pass

    def init_cfg(self):
        # setting_info = {}
        request_type = self.setting_info.get("source_get_request_type")
        # --------source_get-----------
        # init_source_get()
        # --------ftp-----------
        if request_type == 'ftp':
            self.init_ftp_info()
        # --------requests-----------
        elif request_type and request_type.startswith('api'):
            self.init_request_info()
        # ---------sftp-----------
        elif request_type == 'sftp':
            self.init_sftp_info()
        # --------mysql-----------
        self.init_mysql_info()
        # --------mssql-----------
        self.init_mssql_info()
        # --------redis-----------
        self.init_redis_info()
        # --------file_out-----------
        self.init_file_info()
        # ---------parser----------
        # init_parser_info()
        # # --------email-----------
        # if EMAIL_ENABLE:
        self.init_email_info()
        # --------pipeline-----------
        # if PIPELINE_FR_ENABLE:
        self.init_pipeline_info()
        # --------tel-----------
        # if TEL_ENABLE:
        self.init_tel_info()
        #         -----------dpool--------
        # if DPOOL_ENABLE:
        self.init_dpool_info()


def init_all_first():
    global setting_info

    try:
        setting_info = dict(
            project_name=PROJECT_NAME,

            source_get_customize=SOURCE_GET_CUSTOMIZE,
            source_get_date=SOURCE_GET_DATE,
            source_get_date_format=SOURCE_GET_DATE_FORMAT,
            source_get_year=SOURCE_GET_YEAR,
            source_get_request_type=SOURCE_GET_REQUEST_TYPE,
            source_get_connect_id=SOURCE_GET_CONNECT_ID,
            source_get_check=SOURCE_GET_CHECK,

            debug_enable=DEBUG_ENABLE,

        )
        SettingInit(setting_info).init_cfg()

        # setting_info = dict(
        #     project_name=PROJECT_NAME,
        #
        #     source_get_customize=SOURCE_GET_CUSTOMIZE,
        #     source_get_date=SOURCE_GET_DATE,
        #     source_get_date_format=SOURCE_GET_DATE_FORMAT,
        #     source_get_year=SOURCE_GET_YEAR,
        #     source_get_request_type=SOURCE_GET_REQUEST_TYPE,
        #     source_get_connect_id=SOURCE_GET_CONNECT_ID,
        #     source_get_check=SOURCE_GET_CHECK,
        #
        #     sftp_host=SFTP_HOST,
        #     sftp_port=SFTP_PORT,
        #     sftp_user=SFTP_USER,
        #     sftp_password=SFTP_PASSWORD,
        #
        #     ftp_ip=SOURCE_FTP_IP,
        #     ftp_port=SOURCE_FTP_PORT,
        #     ftp_user_id=SOURCE_FTP_USER_ID,
        #     ftp_user_password=SOURCE_FTP_USER_PASSWORD,
        #
        #     request_url_format=SOURCE_URL_FORMAT,
        #     request_url_params=SOURCE_URL_PARAMS,
        #     request_timeout=SOURCE_REQUEST_TIMEOUT,
        #     request_trynum=SOURCE_REQUEST_TRYNUM,
        #
        #     file_download_all=SOURCE_DOWNLOAD_FILES,
        #     file_target_download_path=SOURCE_FILE_TARGET_DOWNLOAD_PATH,
        #     file_target_download_fpath=SOURCE_FILE_TARGET_DOWNLOAD_FPATH,
        #     file_real_target_download_path=SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH,
        #     file_real_target_download_fpath=SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH,
        #
        #     file_unzip_out_path=SOURCE_FILE_UNZIP_OUT_PATH,
        #     file_load_dir_from=SOURCE_LOAD_DIR_FROM,
        #     file_load_file_from=SOURCE_LOAD_FILE_FROM,
        #     file_local_load_dir_cache=SOURCE_LOCAL_LOAD_DIR_CACHE,
        #     file_cache_copy_enable=SOURCE_FILE_CACHE_COPY_ENABLE,
        #     file_cache_del_enable=SOURCE_FILE_CACHE_DEL_ENABLE,
        #     file_load_test_path=SOURCE_FILE_LOAD_TEST_PATH,
        #     file_load_minsize=SOURCE_LOAD_FILE_MINSIZE,
        #     request_load_file_path=SOURCE_REQUEST_LOAD_FILE_PATH,
        #
        #     pipeline_fr_enable=PIPELINE_FR_ENABLE,
        #     pipeline_redis_server_ip=PIPELINE_REDIS_SERVER_IP,
        #     pipeline_redis_server_port=PIPELINE_REDIS_SERVER_PORT,
        #     pipeline_proxy_ip=PIPELINE_PROXY_IP,
        #     pipeline_domain_name=PIPELINE_DOMAIN_NAME,
        #     pipeline_check_key=PIPELINR_CHECK_KEY,
        #     pipeline_project_name=PIPELINE_PROJECT_NAME,
        #     pipeline_fr_fail=PIPELINE_FR_FAIL,
        #
        #     tel_enable=TEL_ENABLE,
        #     tel_contacts=TEL_CONTACTS,
        #     tel_optname=TEL_OPTNAME,
        #
        #     redis_enable=REDIS_ENABLE,
        #     redis_host=REDIS_HOST,
        #     redis_port=REDIS_PORT,
        #     redis_password=REDIS_PASSWORD,
        #     redis_load_db=REDIS_LOAD_DB,
        #     redis_proxy_db=REDIS_PROXY_DB,
        #
        #     email_enable=EMAIL_ENABLE,
        #     email_host=EMAIL_HOST,
        #     email_from=EMAIL_FROM,
        #     email_user_name=EMAIL_USER_NAME,
        #     email_subject=EMAIL_SUBJECT,
        #     email_content=EMAIL_CONTENT,
        #     email_cc=EMAIL_CC,
        #     email_to_list=EMAIL_TO_LIST,
        #     email_file_report=EMAIL_FILE_REPORT,
        #
        #     debug_enable=DEBUG_ENABLE,
        #
        #     source_check_out_data=SOURCE_CHECK_OUT_DATA,
        #     # source_request_type=SOURCE_REQUEST_TYPE,
        #     source_date=SOURCE_DATE,
        #     source_date_format=SOURCE_DATE_FORMAT,
        #     source_year=SOURCE_YEAR,
        #     source_request_timeout=SOURCE_REQUEST_TIMEOUT,
        #     source_request_trynum=SOURCE_REQUEST_TRYNUM,
        #     source_need_ua=SOURCE_NEED_UA,
        #     source_default_ua=SOURCE_DEFAULT_UA,
        #     source_request_auth_name=SOURCE_REQUEST_AUTH_NAME,
        #     source_request_auth_password=SOURCE_REQUEST_AUTH_PASSWORD,
        #
        #     source_url_format=SOURCE_URL_FORMAT,
        #     source_url_params=SOURCE_URL_PARAMS,
        #     source_url_start_page=SOURCE_URL_START_PAGE,
        #     source_url_stop_page_num=SOURCE_URL_STOP_PAGE_NUM,
        #     source_url_pagesize=SOURCE_URL_PAGESIZE,
        #
        #     source_sftp_host=SFTP_HOST,
        #     source_sftp_port=SFTP_PORT,
        #     source_sftp_user=SFTP_USER,
        #     source_sftp_password=SFTP_PASSWORD,
        #
        #     source_ftp_ip=SOURCE_FTP_IP,
        #     source_ftp_port=SOURCE_FTP_PORT,
        #     source_ftp_user_id=SOURCE_FTP_USER_ID,
        #     source_ftp_user_password=SOURCE_FTP_USER_PASSWORD,
        #
        #     # 涉及文件下载路径，业务项目普遍有下载转存需求，这里对不同下载方式下载路径做了区分
        #     # 是否可以统一？暂不统一，看后续业务项目再调整
        #     # 已统一
        #     source_download_files=SOURCE_DOWNLOAD_FILES,
        #     source_file_target_download_path=SOURCE_FILE_TARGET_DOWNLOAD_PATH,
        #     source_file_target_download_fpath=SOURCE_FILE_TARGET_DOWNLOAD_FPATH,
        #     source_real_file_target_download_path=SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH,
        #     source_real_file_target_download_fpath=SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH,
        #
        #     source_file_unzip_out_path=SOURCE_FILE_UNZIP_OUT_PATH,
        #     source_load_dir_from=SOURCE_LOAD_DIR_FROM,
        #     source_load_file_from=SOURCE_LOAD_FILE_FROM,
        #     source_local_load_dir_cache=SOURCE_LOCAL_LOAD_DIR_CACHE,
        #     source_file_cache_copy_enable=SOURCE_FILE_CACHE_COPY_ENABLE,
        #     source_file_cache_del_enable=SOURCE_FILE_CACHE_DEL_ENABLE,
        #     source_file_load_test_path=SOURCE_FILE_LOAD_TEST_PATH,
        #     source_load_file_minsize=SOURCE_LOAD_FILE_MINSIZE,
        #     source_request_load_file_path=SOURCE_REQUEST_LOAD_FILE_PATH,
        #     # source_ftp_target_dir=SOURCE_FTP_TARGET_DIR,
        #     # source_ftp_real_target_dir=SOURCE_FTP_REAL_TARGET_DIR,
        #     #
        #
        #     # source_sftp_output_dir=SOURCE_SFTP_OUTPUT_DIR,
        #     # source_sftp_real_output_dir=SOURCE_SFTP_REAL_OUTPUT_DIR,
        #     # source_sftp_path_test=SOURCE_SFTP_PATH_TEST,
        #     source_sql=SOURCE_SQL,
        #     source_sql_param=SOURCE_SQL_PARAM,
        #
        #     dpool_enable=DPOOL_ENABLE,
        #     dpool_key=DPOOL_KEY,
        #     dpool_jobctl_pool=DPOOL_JOBCTL_POOL,
        #     dpool_load_from_redis_enable=DPOOL_LOAD_FROM_REDIS_ENABLE,
        #
        #     mssqldb_enable=MSSQLDB_ENABLE,
        #     mssqldb_connect_url=MSSQLDB_CONNECT_URL,
        #     mssqldb_table=MSSQLDB_TABLE,
        #
        #     mysql_enable=MYSQL_ENABLE,
        #     mysql_host=MYSQL_HOST,
        #     mysql_port=MYSQL_PORT,
        #     mysql_user=MYSQL_USER,
        #     mysql_password=MYSQL_PASSWORD,
        #     mysql_db_name=MYSQL_DB_NAME,
        #     # mysql_sql=MYSQL_SQL,
        #     # mysql_sql_param=MYSQL_SQL_PARAM,
        #
        #     # parser_date=PARSER_DATE,
        #     # parser_date_format=PARSER_DATE_FORMAT
        #
        # )

    except:
        traceback.print_exc()


def reload_setting(work_path=''):
    global conf
    conf = initialize_config(work_path)
    init_program_base()
    init_all_first()


init_all_first()
