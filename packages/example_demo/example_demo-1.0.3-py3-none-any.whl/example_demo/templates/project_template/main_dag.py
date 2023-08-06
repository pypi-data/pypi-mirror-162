from airflow import DAG
import dataops
from jindefund.pipeline.decorators import win_virtualenv

from {airflow_owner}.{project_name}.env_dag_cfg import DAG_CFGS, CONN_ID, REQUIREMENTS, PIP_INSTALL_OPTIONS, PY_VERSION, \
    PROGRAM_DAG_FOLDER

dataops.turnoff_all_warnings()


# 1. 数据准备及检查 入口
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID, task_id="get_source_info",
                do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def get_source_info(run_path):
    import sys
    sys.path.insert(0, run_path)
    from url_source import UrlSource

    # # 设置传参
    # cus_start_time = kwargs.get("dag_run").conf.get("start_time")
    all_source = UrlSource().load_all_source()
    # all_source_info["load_resource"] = all_source

    return all_source

# 2. 数据下载及解析
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID,
                task_id="download_source_info", do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def hooks_download(all_source, run_path):
    import sys
    sys.path.insert(0, run_path)
    import parser_customize as parser
    from onedatautil.program_process.process_download_parse import DownloadParse

    for sour in all_source:
        DownloadParse(sour, parser).main_process()

    return all_source

# 3. 其他必要的任务（邮件，电话等）


with DAG(
        **DAG_CFGS
) as dag:

    hooks_download(get_source_info(PROGRAM_DAG_FOLDER), run_path=PROGRAM_DAG_FOLDER)

    # source = task_prepare_source >> task_download  # 指定执行顺序
