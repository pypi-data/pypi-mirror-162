# -*- coding: utf-8 -*-

import argparse

# import example_demo.setting as setting
from example_demo.commands.generate import *


def main():
    spider = argparse.ArgumentParser(description="生成器")

    spider.add_argument(
        "-p", "--project", help="创建项目 如 onedatautil create -p <project_name>", metavar=""
    )

    spider.add_argument(
         "--dt", help="项目时间标注",  action="store_true"
    )

    spider.add_argument(
        "-DT", "--download_type", help="项目下载类型 支持 （sftp,ftp,get,post,mysql,redis）如 onedatautil create -p <project_name> -DT sftp", metavar=""
    )

    spider.add_argument(
        "--airflow", help="airflow 项目", action="store_true"
    )
    spider.add_argument(
        "-owner", "--airflow_owner", help="airflow项目开发者", metavar=""
    )
    args = spider.parse_args()


    if args.project:
        GenerateProject().generate(args.project, need_date=args.dt, download_type=args.download_type, airflow_p=args.airflow,airflow_owner=args.airflow_owner)



if __name__ == "__main__":
    main()