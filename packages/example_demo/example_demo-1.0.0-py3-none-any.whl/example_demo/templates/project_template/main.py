# -*- coding: utf-8 -*-
from example_demo import ArgumentParser
from example_demo import ProgramProcess
import url_source as url_s
import parser_customize as parser_c
import click


@click.command()
@click.option('-initDP', '--init_dpool', type=bool, required=False, help='集群项目初始化')
@click.option('-pn', '--project_name', type=str, required=False, help='项目名称')
@click.option('-sd', '--source_date', type=str, required=False, help='数据时间')
@click.option('-ofr', '--only_file_report', type=bool, required=False, help='只监控项目文件状态')
def program_main(**kwargs):
    program = ProgramProcess(url_s=url_s, parser_c=parser_c, **kwargs)
    program.run()


if __name__ == '__main__':
    program_main()
