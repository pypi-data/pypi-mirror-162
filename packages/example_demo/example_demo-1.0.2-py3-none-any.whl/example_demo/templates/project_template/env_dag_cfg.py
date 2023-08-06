import datetime
import pendulum


# [env]
# 连接机器
CONN_ID = '31_win'
# CONN_ID = "dataops@172.30.17.131"
# python环境 版本，需求包
python_env = {
    "py_ver": "",
    "requirements": [],
    "psrp_": CONN_ID
}
# dag 共享目录
DAGS_UNC_FOLDER = r'\\sh-gitlab-ci.jinde.local\airflow-dags'
REQUIREMENTS = ['onedatautil']
PIP_INSTALL_OPTIONS = ['-i', 'http://pypi:8081', '--trusted-host', 'pypi']



# [dag]
# airflow.DAG args
# 项目名称 必填
DAG_ID = ''
DAG_DESCRIPTION = ''

# 项目计划执行时间 支持crontab，但是注意有时区问题，参见下面的文档
# https://codeserver.jinde.local/jdquant/jindefund-airflow/blob/master/docs/schedule.md
DAG_SCHEDULE_INTERVAL = ''
DAG_CATCHUP = False
DAG_START_DATE = pendulum.yesterday()

# 项目运行时间限制
DAGRUN_TIMEOUT = datetime.timedelta(minutes=60)

# 拥有者名称
DAG_OWNER = ''
# dag 权限控制
# eg: {"JD_DATAOPS":{"can_edit", "can_read"}}
DAG_ACCESS_CONTROL = {}

# 分类
DAG_TAG = []

# 是否依赖于过去。如果为True，那么必须要前次的DAG执行成功了，此次的DAG才能执行。默认False
DAG_DEPENDS_ON_PAST = False

# 出问题时，发送报警Email的地址
DAG_EMAIL = []

# 任务失败且重试次数用完时是否发送Email。
DAG_EMAIL_ON_FAILURE = True

# 任务重试时是否发送Email
DAG_EMAIL_ON_RETRY = False

# 失败重试次数
DAG_RETRIES = 1

# 失败重试间隔
DAG_RETRY_DELAY = datetime.timedelta(seconds=60)



def default_options():
    default_args = {
        'owner': DAG_OWNER,
        'depends_on_past': DAG_DEPENDS_ON_PAST,
        'start_date': DAG_START_DATE,
        'email': DAG_EMAIL,
        'email_on_failure': DAG_EMAIL_ON_FAILURE,
        'email_on_retry': DAG_EMAIL_ON_RETRY,
        'retries': DAG_RETRIES,  # 失败重试次数
        'retry_delay': DAG_RETRY_DELAY,  # 失败重试间隔
    }
    return default_args


DAG_CFGS = dict(
    dag_id=DAG_ID,
    default_args=default_options(),
    schedule_interval=DAG_SCHEDULE_INTERVAL,
    dagrun_timeout=DAGRUN_TIMEOUT,
    catchup=DAG_CATCHUP,
)
if DAG_ACCESS_CONTROL:
    DAG_CFGS["access_control"] = DAG_ACCESS_CONTROL
if DAG_TAG:
    DAG_CFGS["tags"] = DAG_TAG
if DAG_DESCRIPTION:
    DAG_CFGS["description"] = DAG_DESCRIPTION