import os
import datetime
import time

import example_demo.commons.common_fun as common
from example_demo.commons.common_cfg import get_cfg_data
from example_demo.configuration import conf

project_name = conf.get("project", "name")
email_file_report = conf.get("email", "file_report")
print(f'init_project_name:{project_name},email_filereport:{email_file_report}')

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


PROJECT_NAME = ''

# [airflow]



# [邮件]
EMAIL_ENABLE = 0
EMAIL_HOST = ''
EMAIL_FROM = ''
EMAIL_USER_NAME = ''
EMAIL_TO_LIST = ''
EMAIL_CC = ''
EMAIL_SUBJECT = ''
EMAIL_CONTENT = ''
EMAIL_FILE_REPORT = True

# [pipeline]
PIPELINE_FR_ENABLE = 0
PIPELINE_REDIS_SERVER_IP = ''
PIPELINE_REDIS_SERVER_PORT = ''
PIPELINE_PROXY_IP = ''
PIPELINE_DOMAIN_NAME = ''
PIPELINR_CHECK_KEY = ''
PIPELINE_PROJECT_NAME = ''
# 是否上报失败文件信息，默认关闭
PIPELINE_FR_FAIL = False

# [tel]
TEL_ENABLE = 0
TEL_CONTACTS = []
TEL_OPTNAME = ''
# TEL_SUB_DATE_TYPE = ''
# TEL_REMIND_INFO = ''
# TEL_TEMPLATE_NO = ''
# TEL_STATUS = ''
# TEL_CALLTIMES = ''
# TEL_MEMO = ''


# [mssqldb]
MSSQLDB_ENABLE = 0
#  r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
MSSQLDB_CONNECT_URL = ''
MSSQLDB_TABLE = ''
# SQLDB_CHECK_SQL

# [mysql]
MYSQL_ENABLE = 0
MYSQL_HOST = ''
MYSQL_PORT = 3306
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DB_NAME = ''
MYSQL_SQL = ''
MYSQL_SQL_PARAM = ''


# [redis]
REDIS_ENABLE = 0
REDIS_HOST = ''
REDIS_PORT = ''
REDIS_PASSWORD = ''
REDIS_LOAD_DB = ''
REDIS_PROXY_DB = ''
#
# REDIS_SLAVER = ''
# REDIS_VALUE0 = ''
# REDIS_VALUE1 = ''

# [dpool]
DPOOL_ENABLE = 0
DPOOL_KEY = ''
DPOOL_JOBCTL_POOL = 'redis://sh-dpool'
DPOOL_LOAD_FROM_REDIS_ENABLE = ''

# [ldb]
LDB_ENABLE = 0
#  r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
LDB_TARGET = ''
#
LDB_SCHEMA = ''

# [debug]
DEBUG_ENABLE = 1

# [clean]
CLEAN_WARNING = ''
CLEAN_ERROR = ''

# [source]
SOURCE_CUSTOMIZE = 0
SOURCE_CHECK_OUT_DATA = 0
SOURCE_DATE = ''
SOURCE_DATE_FORMAT = ''
SOURCE_YEAR = ''
#
SOURCE_REQUEST_TYPE = ''
SOURCE_REQUEST_TIMEOUT = 10
SOURCE_REQUEST_TRYNUM = 3
# reqest请求下载文件路径，通常场景是request请求后，下载转存为文件。默认为空即不需要下载转存，有值时为下载路径，支持直接路径全称也支持格式化{}，比如{source_file_target_download_fpath}
# 这里是有可能会有多个的，另外可能和本地缓存功能一致？
SOURCE_REQUEST_LOAD_FILE_PATH = ''

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
SOURCE_SFTP_HOST = ''
SOURCE_SFTP_PORT = ''
SOURCE_SFTP_USER = ''
SOURCE_SFTP_PASSWORD = ''
# 保留待废弃
SOURCE_SFTP_FILE = ''
SOURCE_SFTP_LOAD_PATH = ''
SOURCE_SFTP_OUT_PATH = ''
SOURCE_SFTP_OUTPUT_DIR = ''
SOURCE_SFTP_REAL_OUTPUT_DIR = ''
SOURCE_SFTP_PATH_TEST = ''

# ftp
SOURCE_FTP_IP = ''
SOURCE_FTP_PORT = ''
SOURCE_FTP_USER_ID = ''
SOURCE_FTP_USER_PASSWORD = ''
# 保留待废弃
SOURCE_FTP_TARGET_DIR_DOWNLOAD = ''
SOURCE_FTP_REAL_TARGET_DIR_DOWNLOAD = ''

# db
SOURCE_SQL = ''
SOURCE_SQL_PARAM = ''

program_config = {}

setting_info = {}


def init_cfg():
    global PROJECT_NAME

    global EMAIL_ENABLE
    global EMAIL_HOST
    global EMAIL_TO_LIST
    global EMAIL_CC
    global EMAIL_SUBJECT
    global EMAIL_CONTENT
    global EMAIL_FROM
    global EMAIL_USER_NAME
    global EMAIL_FILE_REPORT

    global PIPELINE_FR_ENABLE
    global PIPELINE_REDIS_SERVER_IP
    global PIPELINE_REDIS_SERVER_PORT
    global PIPELINE_PROXY_IP
    global PIPELINE_DOMAIN_NAME
    global PIPELINR_CHECK_KEY
    global PIPELINE_PROJECT_NAME
    global PIPELINE_FR_FAIL

    global TEL_ENABLE
    global TEL_CONTACTS
    global TEL_OPTNAME

    global REDIS_ENABLE
    global REDIS_HOST
    global REDIS_PORT
    global REDIS_PASSWORD
    global REDIS_LOAD_DB
    global REDIS_PROXY_DB

    global MYSQL_ENABLE
    global MYSQL_HOST
    global MYSQL_PORT
    global MYSQL_USER
    global MYSQL_PASSWORD
    global MYSQL_DB_NAME
    global MYSQL_SQL
    global MYSQL_SQL_PARAM

    global DPOOL_ENABLE
    global DPOOL_KEY
    global DPOOL_JOBCTL_POOL
    global DPOOL_LOAD_FROM_REDIS_ENABLE

    global LDB_ENABLE
    global LDB_TARGET

    global MSSQLDB_ENABLE
    global MSSQLDB_CONNECT_URL
    global MSSQLDB_TABLE

    global DEBUG_ENABLE

    global SOURCE_CUSTOMIZE
    global SOURCE_CHECK_OUT_DATA
    global SOURCE_REQUEST_TYPE
    global SOURCE_DATE
    global SOURCE_DATE_FORMAT
    global SOURCE_YEAR
    global SOURCE_REQUEST_LOAD_FILE_PATH
    global SOURCE_REQUEST_TIMEOUT
    global SOURCE_REQUEST_TRYNUM
    global SOURCE_NEED_UA
    global SOURCE_DEFAULT_UA
    global SOURCE_REQUEST_AUTH_NAME
    global SOURCE_REQUEST_AUTH_PASSWORD
    global SOURCE_URL_FORMAT
    global SOURCE_URL_PARAMS
    global SOURCE_URL_START_PAGE
    global SOURCE_URL_STOP_PAGE_NUM
    global SOURCE_URL_PAGESIZE

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

    global SOURCE_SFTP_HOST
    global SOURCE_SFTP_PORT
    global SOURCE_SFTP_USER
    global SOURCE_SFTP_PASSWORD
    # global SOURCE_SFTP_OUTPUT_DIR
    # global SOURCE_SFTP_REAL_OUTPUT_DIR
    # global SOURCE_SFTP_PATH_TEST

    global SOURCE_FTP_IP
    global SOURCE_FTP_PORT
    global SOURCE_FTP_USER_ID
    global SOURCE_FTP_USER_PASSWORD
    # global SOURCE_FTP_TARGET_DIR_DOWNLOAD
    # global SOURCE_FTP_REAL_TARGET_DIR_DOWNLOAD

    global SOURCE_SQL
    global SOURCE_SQL_PARAM

    global program_config

    CONFIG_FILE = "project.cfg"
    cfg_path = (os.path.join(os.getcwd(), CONFIG_FILE))
    if not common.check_path(cfg_path):
        # print('no cfg!!')
        return
    program_config = get_cfg_data(cfg_path, need_dict=True)
    PROJECT_NAME = common.try_get(program_config, ["project", "name"])
    PIPELINE_FR_ENABLE = common.try_int(common.try_get(program_config, ["pipeline", "fr_enable"]))
    PIPELINE_REDIS_SERVER_IP = common.try_get(program_config, ["pipeline", "redis_server_ip"])
    PIPELINE_REDIS_SERVER_PORT = common.try_get(program_config, ["pipeline", "redis_server_port"])
    PIPELINE_PROXY_IP = common.try_get(program_config, ["pipeline", "proxy_ip"])
    PIPELINE_DOMAIN_NAME = common.try_get(program_config, ["pipeline", "domain_name"])
    PIPELINR_CHECK_KEY = common.try_get(program_config, ["pipeline", "check_key"])
    PIPELINE_PROJECT_NAME = common.try_get(program_config, ["pipeline", "project_name"])
    pipeline_fr_fail = common.try_get(program_config, ["pipeline", "fr_fail"])
    if pipeline_fr_fail == 'True':
        PIPELINE_FR_FAIL = True

    TEL_ENABLE = common.try_int(common.try_get(program_config, ["tel", "enable"]))
    TEL_CONTACTS = common.try_get(program_config, ["tel", "contacts"])
    if TEL_CONTACTS:
        TEL_CONTACTS = TEL_CONTACTS.split(";")
    TEL_OPTNAME = common.try_get(program_config, ["tel", "optname"])

    REDIS_ENABLE = common.try_int(common.try_get(program_config, ["redis", "enable"]))
    REDIS_HOST = common.try_get(program_config, ["redis", "host"])
    REDIS_PORT = common.try_get(program_config, ["redis", "port"])
    REDIS_PASSWORD = common.try_get(program_config, ["redis", "password"])
    REDIS_LOAD_DB = common.try_get(program_config, ["redis", "load_db"])
    REDIS_PROXY_DB = common.try_get(program_config, ["redis", "proxy_db"])

    EMAIL_ENABLE = common.try_int(common.try_get(program_config, ["email", "enable"]))
    EMAIL_HOST = common.try_get(program_config, ["email", "host"])
    EMAIL_FROM = common.try_get(program_config, ["email", "from"])
    EMAIL_USER_NAME = common.try_get(program_config, ["email", "user_name"])
    EMAIL_TO_LIST = common.try_get(program_config, ["email", "to"])
    EMAIL_CC = common.try_get(program_config, ["email", "cc"])
    if EMAIL_TO_LIST:
        EMAIL_TO_LIST = EMAIL_TO_LIST.split(";")
    if EMAIL_CC:
        EMAIL_CC = EMAIL_CC.split(";")
    EMAIL_SUBJECT = common.try_get(program_config, ["email", "subject"])
    EMAIL_CONTENT = common.try_get(program_config, ["email", "content"])
    email_file_report = common.try_get(program_config, ["email", "file_report"])
    if email_file_report == 'False':
        EMAIL_FILE_REPORT = False

    DEBUG_ENABLE = common.try_int(common.try_get(program_config, ["debug", "enable"]))
    # --------source-----------
    SOURCE_CUSTOMIZE = common.try_get(program_config, ["source", "customize"])
    SOURCE_CHECK_OUT_DATA = common.try_int(common.try_get(program_config, ["source", "check_out_data"]))
    SOURCE_DATE = common.try_get(program_config, ["source", "date"])
    SOURCE_DATE_FORMAT = common.try_get(program_config, ["source", "date_format"])
    if not SOURCE_DATE_FORMAT:
        SOURCE_DATE_FORMAT = '%Y-%m-%d'
    # 默认时间前一天， ；支持 直接输入的 %Y-%m-%d 是否支持识别切换工作日和正常日期
    # 时间，支持 直接输入的 %Y-%m-%d；workday 前一天工作日；day（默认） 前一天;

    if not SOURCE_DATE:
        SOURCE_DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
            SOURCE_DATE_FORMAT)
    elif SOURCE_DATE == 'now':
        SOURCE_DATE = datetime.datetime.now().strftime(SOURCE_DATE_FORMAT)
    time_date = time.strptime(SOURCE_DATE, SOURCE_DATE_FORMAT)
    SOURCE_YEAR = time_date.tm_year

    SOURCE_REQUEST_TYPE = common.try_get(program_config, ["source", "request_type"])
    source_request_timeout = common.try_int(common.try_get(program_config, ["source", "request_timeout"]))
    if source_request_timeout:
        SOURCE_REQUEST_TIMEOUT = source_request_timeout
    source_request_trynum = common.try_int(common.try_get(program_config, ["source", "request_trynum"]))
    if source_request_trynum:
        SOURCE_REQUEST_TRYNUM = source_request_trynum
    SOURCE_NEED_UA = common.try_get(program_config, ["source", "need_ua"])
    SOURCE_DEFAULT_UA = common.try_get(program_config, ["source", "default_ua"])
    SOURCE_REQUEST_AUTH_NAME = common.try_get(program_config, ["source", "request_auth_name"])
    SOURCE_REQUEST_AUTH_PASSWORD = common.try_get(program_config, ["source", "request_auth_password"])

    SOURCE_URL_FORMAT = common.try_get(program_config, ["source", "url_format"])
    url_params = common.try_get(program_config, ["source", "url_params"])
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

    SOURCE_URL_START_PAGE = common.try_int(common.try_get(program_config, ["source", "url_start_page"]))
    SOURCE_URL_STOP_PAGE_NUM = common.try_int(common.try_get(program_config, ["source", "url_stop_page_num"]))
    SOURCE_URL_PAGESIZE = common.try_int(common.try_get(program_config, ["source", "url_pagesize"]))

    SOURCE_SFTP_HOST = common.try_get(program_config, ["source", "sftp_host"])
    SOURCE_SFTP_PORT = common.try_int(common.try_get(program_config, ["source", "sftp_port"]))
    SOURCE_SFTP_USER = common.try_get(program_config, ["source", "sftp_user"])
    SOURCE_SFTP_PASSWORD = common.try_get(program_config, ["source", "sftp_password"])
    # SFTP_USER_2 = common.try_get(program_config, ["url_source", "sftp_user_2"])
    # SFTP_PASSWORD_2 = common.try_get(program_config, ["url_source", "sftp_user_password_ase2"])
    if SOURCE_SFTP_USER and SOURCE_SFTP_PASSWORD:
        SOURCE_SFTP_USER = SOURCE_SFTP_USER.split(";")
        SOURCE_SFTP_PASSWORD = SOURCE_SFTP_PASSWORD.split(";")
    # SOURCE_SFTP_OUTPUT_DIR = common.try_get(program_config, ["source", "sftp_output_dir"])
    # SOURCE_SFTP_PATH_TEST = common.try_get(program_config, ["source", "sftp_path_test"])
    # SOURCE_SFTP_REAL_OUTPUT_DIR = common.try_get(program_config, ["source", "sftp_real_output_dir"])

    SOURCE_FTP_IP = common.try_get(program_config, ["source", "ftp_ip"])
    SOURCE_FTP_PORT = common.try_int(common.try_get(program_config, ["source", "ftp_port"]))
    SOURCE_FTP_USER_ID = common.try_get(program_config, ["source", "ftp_user_id"])
    SOURCE_FTP_USER_PASSWORD = common.try_get(program_config, ["source", "ftp_user_password"])
    # SOURCE_FTP_DIR = common.try_get(program_config, ["source", "ftp_dir"])
    # SOURCE_FTP_TARGET_DIR = common.try_get(program_config, ["source", "ftp_target_dir"])
    # SOURCE_FTP_REAL_TARGET_DIR = common.try_get(program_config, ["source", "ftp_real_target_dir"])

    SOURCE_DOWNLOAD_FILES = common.try_get(program_config, ["source", "download_files"])
    if SOURCE_DOWNLOAD_FILES:
        SOURCE_DOWNLOAD_FILES = SOURCE_DOWNLOAD_FILES.split(";")
        SOURCE_DOWNLOAD_FILES = [file for file in SOURCE_DOWNLOAD_FILES if file]
    SOURCE_FILE_TARGET_DOWNLOAD_PATH = common.try_get(program_config, ["source", "file_target_download_path"])
    SOURCE_FILE_TARGET_DOWNLOAD_FPATH = common.try_get(program_config, ["source", "file_target_download_fpath"])
    if SOURCE_DOWNLOAD_FILES and SOURCE_FILE_TARGET_DOWNLOAD_PATH and not SOURCE_FILE_TARGET_DOWNLOAD_FPATH:
        SOURCE_FILE_TARGET_DOWNLOAD_FPATH = common.parse_list_files_join_path(SOURCE_FILE_TARGET_DOWNLOAD_PATH,
                                                                              SOURCE_DOWNLOAD_FILES)

    SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH = common.try_get(program_config, ["source", "real_file_target_download_path"])
    SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH = common.try_get(program_config,
                                                            ["source", "real_file_target_download_fpath"])
    if SOURCE_DOWNLOAD_FILES and SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH and not SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH:
        SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH = common.parse_list_files_join_path(
            SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH,
            SOURCE_DOWNLOAD_FILES, diff_os=True)
    SOURCE_FILE_UNZIP_OUT_PATH = common.try_get(program_config, ["source", "file_unzip_out_path"])
    SOURCE_LOAD_DIR_FROM = common.try_get(program_config, ["source", "load_dir_from"])
    source_load_file_from = common.try_get(program_config, ["source", "load_file_from"])
    if SOURCE_DOWNLOAD_FILES and SOURCE_LOAD_DIR_FROM and not source_load_file_from:
        SOURCE_LOAD_FILE_FROM = common.parse_list_files_join_path(SOURCE_LOAD_DIR_FROM, SOURCE_DOWNLOAD_FILES)

    SOURCE_LOCAL_LOAD_DIR_CACHE = common.try_get(program_config, ["source", "local_load_dir_cache"])
    source_file_cache_copy_enable = common.try_get(program_config, ["source", "file_cache_copy_enable"])
    if source_file_cache_copy_enable == 'True':
        SOURCE_FILE_CACHE_COPY_ENABLE = True
    source_file_cache_del_enable = common.try_get(program_config, ["source", "file_cache_del_enable"])
    if source_file_cache_del_enable == 'True':
        SOURCE_FILE_CACHE_DEL_ENABLE = True

    SOURCE_FILE_LOAD_TEST_PATH = common.try_get(program_config, ["source", "file_load_test_path"])
    SOURCE_LOAD_FILE_MINSIZE = common.try_int(
        common.try_get(program_config, ["source", "load_file_minsize"], default_value=0))
    SOURCE_REQUEST_LOAD_FILE_PATH = common.try_get(program_config, ["source", "request_load_file_path"])

    SOURCE_SQL = common.try_get(program_config, ["source", "sql"])
    SOURCE_SQL_PARAM = common.try_get(program_config, ["source", "sql_param"])
    # eg : sql = select alertid,subject,sendto,clock from alerts where subject
    # like '%{subject_like}%' and (sendto like '%{receiver_like}%') order by clock desc limit 0,1

    if SOURCE_SQL_PARAM and SOURCE_SQL:
        pass

    DPOOL_ENABLE = common.try_int(common.try_get(program_config, ["dpool", "enable"]))
    DPOOL_KEY = common.try_get(program_config, ["dpool", "key"])
    dpool_jobctl_pool = common.try_get(program_config, ["dpool", "jobctl_pool"])
    if dpool_jobctl_pool:
        DPOOL_JOBCTL_POOL = dpool_jobctl_pool
    DPOOL_LOAD_FROM_REDIS_ENABLE = common.try_int(common.try_get(program_config, ["dpool", "load_from_redis_enable"]))

    MSSQLDB_ENABLE = common.try_int(common.try_get(program_config, ["mssqldb", "enable"]))
    MSSQLDB_CONNECT_URL = common.try_get(program_config, ["mssqldb", "connect_url"])
    MSSQLDB_TABLE = common.try_get(program_config, ["mssqldb", "table"])

    MYSQL_ENABLE = common.try_int(common.try_get(program_config, ["mysql", "enable"]))
    MYSQL_HOST = common.try_get(program_config, ["mysql", "host"])
    MYSQL_PORT = common.try_int(common.try_get(program_config, ["mysql", "port"])) if common.try_get(program_config, ["mysql", "port"]) else 3306
    MYSQL_USER = common.try_get(program_config, ["mysql", "user"])
    MYSQL_PASSWORD = common.try_get(program_config, ["mysql", "password"])
    MYSQL_DB_NAME = common.try_get(program_config, ["mysql", "db"])
    MYSQL_SQL = common.try_get(program_config, ["mysql", "sql"])
    MYSQL_SQL_PARAM = common.try_get(program_config, ["mysql", "sql_param"])



def initialize():
    pass

# 封装成字典对象 &  直接内置变量 &   ConfigParser()

try:
    init_cfg()
    setting_info = dict(
        project_name=PROJECT_NAME,

        pipeline_fr_enable=PIPELINE_FR_ENABLE,
        pipeline_redis_server_ip=PIPELINE_REDIS_SERVER_IP,
        pipeline_redis_server_port=PIPELINE_REDIS_SERVER_PORT,
        pipeline_proxy_ip=PIPELINE_PROXY_IP,
        pipeline_domain_name=PIPELINE_DOMAIN_NAME,
        pipeline_check_key=PIPELINR_CHECK_KEY,
        pipeline_project_name=PIPELINE_PROJECT_NAME,
        pipeline_fr_fail=PIPELINE_FR_FAIL,

        tel_enable=TEL_ENABLE,
        tel_contacts=TEL_CONTACTS,
        tel_optname=TEL_OPTNAME,

        redis_enable=REDIS_ENABLE,
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT,
        redis_password=REDIS_PASSWORD,
        redis_load_db=REDIS_LOAD_DB,
        redis_proxy_db=REDIS_PROXY_DB,

        email_enable=EMAIL_ENABLE,
        email_host=EMAIL_HOST,
        email_from=EMAIL_FROM,
        email_user_name=EMAIL_USER_NAME,
        email_subject=EMAIL_SUBJECT,
        email_content=EMAIL_CONTENT,
        email_cc=EMAIL_CC,
        email_to_list=EMAIL_TO_LIST,
        email_file_report=EMAIL_FILE_REPORT,

        debug_enable=DEBUG_ENABLE,

        source_customize=SOURCE_CUSTOMIZE,
        source_check_out_data=SOURCE_CHECK_OUT_DATA,
        source_request_type=SOURCE_REQUEST_TYPE,
        source_date=SOURCE_DATE,
        source_date_format=SOURCE_DATE_FORMAT,
        source_year=SOURCE_YEAR,
        source_request_timeout=SOURCE_REQUEST_TIMEOUT,
        source_request_trynum=SOURCE_REQUEST_TRYNUM,
        source_need_ua=SOURCE_NEED_UA,
        source_default_ua=SOURCE_DEFAULT_UA,
        source_request_auth_name=SOURCE_REQUEST_AUTH_NAME,
        source_request_auth_password=SOURCE_REQUEST_AUTH_PASSWORD,

        source_url_format=SOURCE_URL_FORMAT,
        source_url_params=SOURCE_URL_PARAMS,
        source_url_start_page=SOURCE_URL_START_PAGE,
        source_url_stop_page_num=SOURCE_URL_STOP_PAGE_NUM,
        source_url_pagesize=SOURCE_URL_PAGESIZE,

        source_sftp_host=SOURCE_SFTP_HOST,
        source_sftp_port=SOURCE_SFTP_PORT,
        source_sftp_user=SOURCE_SFTP_USER,
        source_sftp_password=SOURCE_SFTP_PASSWORD,

        source_ftp_ip=SOURCE_FTP_IP,
        source_ftp_port=SOURCE_FTP_PORT,
        source_ftp_user_id=SOURCE_FTP_USER_ID,
        source_ftp_user_password=SOURCE_FTP_USER_PASSWORD,

        # 涉及文件下载路径，业务项目普遍有下载转存需求，这里对不同下载方式下载路径做了区分
        # 是否可以统一？暂不统一，看后续业务项目再调整
        # 已统一
        source_download_files=SOURCE_DOWNLOAD_FILES,
        source_file_target_download_path=SOURCE_FILE_TARGET_DOWNLOAD_PATH,
        source_file_target_download_fpath=SOURCE_FILE_TARGET_DOWNLOAD_FPATH,
        source_real_file_target_download_path=SOURCE_REAL_FILE_TARGET_DOWNLOAD_PATH,
        source_real_file_target_download_fpath=SOURCE_REAL_FILE_TARGET_DOWNLOAD_FPATH,

        source_file_unzip_out_path=SOURCE_FILE_UNZIP_OUT_PATH,
        source_load_dir_from=SOURCE_LOAD_DIR_FROM,
        source_load_file_from=SOURCE_LOAD_FILE_FROM,
        source_local_load_dir_cache=SOURCE_LOCAL_LOAD_DIR_CACHE,
        source_file_cache_copy_enable=SOURCE_FILE_CACHE_COPY_ENABLE,
        source_file_cache_del_enable=SOURCE_FILE_CACHE_DEL_ENABLE,
        source_file_load_test_path=SOURCE_FILE_LOAD_TEST_PATH,
        source_load_file_minsize=SOURCE_LOAD_FILE_MINSIZE,
        source_request_load_file_path=SOURCE_REQUEST_LOAD_FILE_PATH,
        # source_ftp_target_dir=SOURCE_FTP_TARGET_DIR,
        # source_ftp_real_target_dir=SOURCE_FTP_REAL_TARGET_DIR,
        #

        # source_sftp_output_dir=SOURCE_SFTP_OUTPUT_DIR,
        # source_sftp_real_output_dir=SOURCE_SFTP_REAL_OUTPUT_DIR,
        # source_sftp_path_test=SOURCE_SFTP_PATH_TEST,
        source_sql=SOURCE_SQL,
        source_sql_param=SOURCE_SQL_PARAM,

        dpool_enable=DPOOL_ENABLE,
        dpool_key=DPOOL_KEY,
        dpool_jobctl_pool=DPOOL_JOBCTL_POOL,
        dpool_load_from_redis_enable=DPOOL_LOAD_FROM_REDIS_ENABLE,

        mssqldb_enable=MSSQLDB_ENABLE,
        mssqldb_connect_url=MSSQLDB_CONNECT_URL,
        mssqldb_table=MSSQLDB_TABLE,

        mysql_enable=MYSQL_ENABLE,
        mysql_host=MYSQL_HOST,
        mysql_port=MYSQL_PORT,
        mysql_user=MYSQL_USER,
        mysql_password=MYSQL_PASSWORD,
        mysql_db_name=MYSQL_DB_NAME,
        # mysql_sql=MYSQL_SQL,
        # mysql_sql_param=MYSQL_SQL_PARAM,

    )

except:
    pass
