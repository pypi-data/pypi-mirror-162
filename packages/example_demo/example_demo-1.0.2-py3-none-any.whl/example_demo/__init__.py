# -*- coding: UTF-8 -*-
import argparse
import datetime
import os
import sys
import re
sys.path.insert(0, re.sub(r"([\\/]items$)|([\\/]spiders$)", "", os.getcwd()))
print(os.getcwd())
__all__ = [

    "ArgumentParser",
]

def main():
    # from commands import download
    # download.download('ase2', '20200615')
    parser = argparse.ArgumentParser(prog='example_demo', description='')
    parser.add_argument("--download", help=u"下载文件", action="store_true")
    parser.add_argument("--date", help=u"下载目标的日期(eg:20200101),default yesterday",
                        default='', type=str)
    parser.add_argument("--data_type", help=u"下载数据类型(eg: barra, ase2, cxe1, cne5), default:barra",
                        default='barra', type=str)
    parser.add_argument("--generate", help=u'生成项目', action="store_true")
    parser.add_argument("--gen", help=u'生成项目', action="store_true")

    options = parser.parse_args()
    print(options)
    if options.gen:
        print('test_date')
    # if options.download:
    #     from .commands import download
    #     if options.date == '':
    #         options.date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    #     print('download options : ' + str(options))
    #     download.download(options)
    # else:
    #     print("invalid argument")
    #     parser.print_usage()

from example_demo.utils.custom_argparsers import ArgumentParser
from example_demo.program_process.process_work import ProgramProcess
if __name__ == "__main__":
    main()
