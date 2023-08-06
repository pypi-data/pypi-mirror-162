from airflow import DAG

from airflow.operators.python import PythonVirtualenvOperator
from env_dag_cfg import DAG_CFGS, CONN_ID, REQUIREMENTS, PIP_INSTALL_OPTIONS, DAGS_UNC_FOLDER

# 1. 数据准备及检查 入口
# @task.virtualenv(**python_env)
def get_source_info(**kwargs):
    from url_source import UrlSource
    # 设置传参
    cus_start_time = kwargs.get("dag_run").conf.get("start_time")

    all_source = UrlSource().load_all_source()
    kwargs.get("dag_run").conf["load_resource"] = all_source

    print(f'find_all_source:{len(all_source)}')
    return all_source


def task_get_source_info(dag):
    # task = PythonOperator(
    #     task_id='get_source_info',
    #     python_callable=get_source_info,  # 指定要执行的函数
    #     dag=dag,
    #     op_kwargs=dag.params
    # )
    task = PythonVirtualenvOperator(task_id="get_source_info", psrp_conn_id=CONN_ID, python_callable=get_source_info, requirements=['onedatautil', 'apache-airflow==2.3.2'], do_xcom_push=False)

    return task


# 2. 数据下载及解析
# @task.virtualenv(**python_env)
def hooks_download(**kwargs):
    from onedatautil.request_downloader.airflow_downloader_hooks import source_hooks_downloader
    resource = kwargs.get("dag_run").conf.get("load_resource")
    for sour in resource:
        download_res = source_hooks_downloader(sour)
        sour["download_res"] = download_res

    kwargs.get("dag_run").conf["load_resource"] = resource


def task_download_parse(dag):
    # task = PythonOperator(
    #     task_id='download_resource',
    #     python_callable=hooks_download,  # 指定要执行的函数
    #     dag=dag,
    #     op_kwargs=dag.params
    # )
    task = PythonVirtualenvOperator(task_id="download_resource", psrp_conn_id=CONN_ID, python_callable=hooks_download, requirements=['onedatautil', 'apache-airflow==2.3.2'], do_xcom_push=False)

    return task

# 3. 其他必要的任务（邮件，电话等）


# * 7-23 * * *
with DAG(
        **DAG_CFGS
) as dag:
    # init_env_task = set_env(dag)
    task_prepare_source = task_get_source_info(dag)
    # task_download = task_download_parse(dag)
    # winrm_hook = WinRMHook(ssh_conn_id="zhangyf_win", transport='ntlm')
    # main_task = main_program_task(dag)
    # email_task = emailutil_task(dag)
    # get_source_info >> hooks_download  # 指定执行顺序
