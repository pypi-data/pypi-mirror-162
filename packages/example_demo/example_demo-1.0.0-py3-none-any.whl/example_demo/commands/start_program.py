# -*- coding: utf-8 -*-

import argparse


def main():
    program = argparse.ArgumentParser(description="启动")

    program.add_argument(
        "-init", "--project", help="创建项目 如 onedatautil create -p <project_name>", metavar=""
    )

    program.add_argument(
         "--dt", help="项目时间标注",  action="store_true"
    )


    args = program.parse_args()


    # if args.project:
    #     GenerateProject().generate(args.project, args.dt)
