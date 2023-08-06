# -*- coding: utf-8 -*-
import os
import time
import traceback
import shutil
import json
import re
import copy
from example_demo.program_process.process_sftp import SftpProcess
from example_demo.program_process.process_ftp import FtpProcess
from example_demo.program_process.process_request import RequestProcess

import example_demo.setting as setting
import example_demo.commons.common_fun as common
from example_demo.monitor.monitor_signal_alert import send_mail, pipe_monitor_file
from example_demo.utils.redis_client import connect_redis
from example_demo.utils.jobctl import JobCtl


class ProgramProcess:
    def __init__(self, url_s=None, parser_c=None, **kwargs):

        self.debug = setting.DEBUG_ENABLE
        self.url_customize = setting.SOURCE_GET_CUSTOMIZE
        self.request_type = setting.SOURCE_GET_REQUEST_TYPE
        self.dpool_enable = setting.DPOOL_ENABLE
        self.url_s = url_s
        self.parser_c = parser_c
        self.init_dpool = kwargs.get("init_dpool")
        self.setting_info = setting.setting_info
        self.only_file_report = False
        if 'only_file_report' in kwargs and kwargs.get("only_file_report"):
            self.only_file_report = True

        self.init_kwargs(kwargs)
        self.file_content_email = ''
        # 是否需要检查输出数据已存在
        self.source_get_check = self.setting_info.get("source_get_check")
        self.process = kwargs.get("process")

    # 初始化入参，覆盖更新配置参数
    def init_kwargs(self, kwargs):
        for k, v in kwargs.items():
            if self.setting_info.get(k) and v:
                if self.debug:
                    print('__init_:%s,%s' % (k, v))
                self.setting_info[k] = v

    def run(self):
        # 1.整理数据源
        # list 自定义，非自定义（模板cfg）的处理
        url_source = self.parse_url_cfg() if not self.url_customize else self.url_s.UrlSource(
            debug=self.debug, setting_info=self.setting_info).load_all_source()

        # 2.检查是否需查看数据已有,有的话直接结束；没有的话可能是部分没有，需更新数据源
        # 这步包括了only检查文件状态 的模式
        if self.source_get_check:
            process_start = True if not self.only_file_report else False
            all_has, left_url_source = self.outdata_check(url_source, process_start)
            if all_has:
                # print('program has over')
                return
            url_source = left_url_source
            if self.only_file_report:
                return

        if self.process == 'source_prepare':

            return
        # 是否集群初始化任务
        if self.init_dpool:
            return self.init_dpool_program(self.setting_info)
        if self.dpool_enable:
            return self.dpool_program(url_source)
        # 正式流程(包括 1.下载请求数据（文件），2.处理得到的数据（文件），3.常规通用化的处理（邮件，文件上报，程序收尾的处理）
        self.program_process(url_source)

    def parse_url_cfg(self):
        url_source = {}
        all_source = []
        for k, v in self.setting_info.items():
            if k.startswith("source"):
                url_source[k] = v
        # 如果是集群初始化任务，需要初始化下dpool参数
        if self.dpool_enable:
            dpool_key = self.setting_info.get("dpool_key")
            dpool_key = setting.format_params(dpool_key, self.setting_info)
            self.setting_info["dpool_key"] = dpool_key

        # ------------url
        url_params = url_source.get("source_url_params", {})
        url_format = url_source.get("source_url_format")
        url_format = setting.format_params(url_format, self.setting_info)

        if url_params:
            for k, v in url_params.items():
                # v = setting.format_params(v, self.setting_info)
                # url_params[k] = v
                if v.startswith("{") and v.endswith("}"):
                    v_para = v[1:-1]
                    if url_source.get(v_para):
                        url_params[k] = url_source.get(v_para)

        if url_params and url_format:
            url = common.parse_url_join(url_format, url_params)
            url_source["url"] = url

        # path
        # fpath 可能不是那么有必要，直接组合 source_file_target_download_path + file_download ？
        source_local_load_dir_cache = url_source.get("source_local_load_dir_cache", '')
        source_file_target_download_path = url_source.get("source_file_target_download_path")
        source_file_target_download_fpath = url_source.get("source_file_target_download_fpath")
        source_real_file_target_download_path = url_source.get("source_real_file_target_download_path")
        source_real_file_target_download_fpath = url_source.get("source_real_file_target_download_fpath")
        path_params = re.findall('\{(.*?)\}', source_file_target_download_path)
        has_update = False
        for path_param in path_params:
            if url_source.get(path_param):
                has_update = True
                source_local_load_dir_cache = source_local_load_dir_cache.replace('{%s}' % path_param,
                                                                                  str(url_source.get(path_param)))
                source_file_target_download_path = source_file_target_download_path.replace('{%s}' % path_param,
                                                                                            str(url_source.get(
                                                                                                path_param)))
                source_real_file_target_download_path = source_real_file_target_download_path.replace(
                    '{%s}' % path_param, str(url_source.get(path_param)))
                source_file_target_download_fpath = [f.replace('{%s}' % path_param, str(url_source.get(path_param))) for
                                                     f in source_file_target_download_fpath]

                source_real_file_target_download_fpath = [
                    f.replace('{%s}' % path_param, str(url_source.get(path_param))) for f in
                    source_real_file_target_download_fpath]
        if has_update:
            url_source["source_local_load_dir_cache"] = source_local_load_dir_cache
            url_source["source_file_target_download_path"] = source_file_target_download_path
            url_source["source_file_target_download_fpath"] = source_file_target_download_fpath
            url_source["source_real_file_target_download_path"] = source_real_file_target_download_path
            url_source["source_real_file_target_download_fpath"] = source_real_file_target_download_fpath

        # file_path
        source_download_files = url_source.get("source_download_files")
        source_load_file_from = url_source.get("source_load_file_from")

        source_sql = url_source.get("source_sql")
        # mk:mv1,nk:nv1;mk
        source_sql_param = url_source.get("source_sql_param", "")
        all_sqls = []
        if source_sql:
            source_sql_all_param = re.findall('\{(.*?)\}', source_sql)
            all_sql_params = []
            if source_sql_param:
                sql_params = source_sql_param.split(";")
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
                    if url_source.get(base_param):
                        source_sql = source_sql.replace("{%s}" % base_param, str(url_source.get(base_param)))
            for final_param in all_sql_params:
                c_source = copy.deepcopy(source_sql)
                for k, v in final_param.items():
                    if "{%s}" % k in c_source:
                        c_source = c_source.replace("{%s}" % k, str(v))
                all_sqls.append(c_source)
            if not all_sqls:
                all_sqls.append(source_sql)
            url_source["all_sqls_get"] = all_sqls
        if source_download_files:
            for ind, file in enumerate(source_download_files):
                source = copy.deepcopy(url_source)
                value_list = re.findall('\{(.*?)\}', file)
                file_path = source_file_target_download_fpath[ind]
                real_file_path = source_real_file_target_download_fpath[ind]
                load_file_from = ''
                if len(source_load_file_from) >= ind + 1:
                    load_file_from = source_load_file_from[ind]
                # source_request_load_file_path = source.get("source_request_load_file_path")
                # has_update = False
                for v in value_list:
                    if url_source.get(v):
                        file = file.replace('{%s}' % v, str(url_source.get(v)))
                        file_path = file_path.replace('{%s}' % v, str(url_source.get(v)))
                        real_file_path = real_file_path.replace('{%s}' % v, str(url_source.get(v)))
                        load_file_from = load_file_from.replace('{%s}' % v, str(url_source.get(v)))
                        # has_update = True
                # if has_update:
                source["file_download"] = file
                source["source_file_target_download_fpath"] = file_path
                source["source_real_file_target_download_fpath"] = real_file_path
                source["source_load_file_from"] = load_file_from

                all_source.append(source)

        else:
            all_source = [url_source]
        return all_source

    def outdata_check(self, url_source, process_start=True):
        # 输出数据的检查：包含两种文件类型和数据库数据
        # 有自定义的情况直接使用
        if self.url_s.UrlSource().check_outdata(url_source):
            return self.url_s.UrlSource().check_outdata(url_source)
        #     没有的话，模板支持文件类型的检查；数据库类型需设定查询sql,并且取出后可能有一定的提取处理逻辑，暂不开放模板
        all_has, url_source = self.file_report_process(url_source, process_start=process_start)

        return all_has, url_source

    def program_process(self, url_source):
        # 这里request_type 可以外部自定义细化到每个sour
        # all_has, url_source = self.file_report_process(url_source, process_start=True)
        sour_index = 1
        project_name = self.setting_info.get("project_name")

        for sour in url_source:
            source_real_file_target_download_fpath = sour.get("file_real_target_download_fpath") or sour.get("source_real_file_target_download_fpath")
            process_res = False
            parse_customize = self.parser_c.ParseCustomize()
            source = copy.deepcopy(self.setting_info)
            source.update(sour)
            request_type = source.get("source_get_request_type")
            sqldb_to_table = source.get("sqldb_to_table")

            if self.debug:
                print(source)
            if request_type in ("sftp", "ftp"):
                process_res = self.download_direct(request_type, source, parse_customize)

            elif request_type.startswith('api'):
                self.api_process(source, parse_customize, request_type)
            elif request_type in ('mysql', 'redis', 'mssql'):
                self.load_from_db_process(source, parse_customize, request_type)
            if parse_customize.final_parse_enable:
                process_res = parse_customize.final_parse(source)
            # else:
            self.parse_normal_monitor(process_res, source)
            if sqldb_to_table and process_res:
                source["download_in_db"] = True
            # if url_source.get("pipeline_check_key") and not self.debug:
            #     self.parse_normal_monitor(file_result, url_source)

            process_message = f'项目：{project_name}，{sour_index}/{len(url_source)},target_file_path:{source_real_file_target_download_fpath},success over!'
            if self.debug:
                print(process_message)

        if self.source_get_check:
            all_has, left_url_source = self.outdata_check(url_source, process_start=False)

            # all_has, url_source = self.file_report_process(url_source)

    def program_process_one(self, sour):
        process_res = False
        parse_customize = self.parser_c.ParseCustomize()
        request_type = self.request_type if not sour.get("source_get_request_type") else sour.get("source_get_request_type")
        source = copy.deepcopy(self.setting_info)
        source.update(sour)

        sqldb_to_table = source.get("sqldb_to_table")

        if self.debug:
            print(source)
        if request_type in ("sftp", "ftp"):
            process_res = self.download_direct(request_type, source, parse_customize)

        elif request_type.startswith('api'):
            self.api_process(source, parse_customize, request_type)

        if parse_customize.final_parse_enable:
            process_res = parse_customize.final_parse(sour)
        # else:
        self.parse_normal_monitor(process_res, source)
        if sqldb_to_table and process_res:
            sour["download_in_db"] = True

    def download_direct(self, request_type, source, parse_customize):
        '''
        直接下载文件落地的抓取（ftp,sftp,request请求后转存文件的方式）
        通常落地
        （若有）对文件的自定义的处理(parse_one)
        常规收尾处理（缓存copy & del,文件上报，邮件发送)
        '''
        download_res = False
        if request_type == 'sftp':
            download_res = self.sftp_download_process(source)
        elif request_type == 'ftp':
            download_res = self.ftp_download_process(source)
        # 这里同样可能出现对单一文件的处理
        # if parse_customize.parse_customize_one

        return download_res

    # 集群流程
    def init_dpool_program(self, setting_info):
        all_items = self.url_s.get_dpool_init_items(setting_info)
        load_db = setting_info.get("redis_load_db")
        dpool_key = setting_info.get("dpool_key")
        jobctl_pool = setting_info.get("dpool_jobctl_pool")
        if self.debug:
            return

        redis_client = connect_redis(load_db)
        for seeder in all_items:
            redis_client.lpush(dpool_key, json.dumps(seeder))

        with JobCtl(jobctl_pool) as ctl:
            ctl.run_pyfile('main.py', name=dpool_key,
                           files=['main.py', 'parser_sustomize.py', 'project.cfg', 'url_source.py'])

    def dpool_program(self, url_source):

        # 获取队列
        dpool_key = self.setting_info.get("dpool_key")
        load_db = self.setting_info.get("redis_load_db")
        redis_client = connect_redis(load_db)
        format_sour = url_source[0]
        if self.debug:
            sour = {'code': '603863', 'max_date': '2022-06-06 12:46:00', 'script': None, 'request_func': None,
                    'retry': 0, 'max_retry': 3, 'task_key': 'guba_20220606'}
            c_format_sour = copy.deepcopy(format_sour)
            sour = self.url_s.UrlSource(sour).load_source_dpool(c_format_sour)
            self.program_process_one(sour)

            # sour = self.url_s.UrlSource(sour).load_source_dpool()
            # parse_customize = self.parser_c.ParseCustomize()
            # self.api_process(sour, parse_customize)
        else:
            while redis_client.llen(dpool_key) > 0:
                try:
                    sour = redis_client.lpop(dpool_key)
                    sour = json.loads(sour)
                    sour = self.url_s.UrlSource(sour).load_source_dpool(format_sour)
                    self.program_process_one(sour)
                    # parse_customize = self.parser_c.ParseCustomize()
                    #
                    # self.api_process(sour, parse_customize)
                    # # get_data(deepcopy(seeder))
                except Exception as ex:
                    traceback.print_exc()
                    # print('get seeder from redis fail. ', ex, download_config['redis_key'])
                    # with open(log_file, 'w') as obj:
                    #     obj.write('get seeder from redis fail. ' + str(ex) + " " + str(download_config['redis_key']))
        redis_client.close()

    def prepare_sftp_request(self, sour):
        request_info = sour.get("request_info", {})
        sftp_user_index = sour.get("sftp_user_index", 1)
        sftp_user_list = sour.get("sftp_user") or sour.get("source_sftp_user")
        sftp_password_list = sour.get("sftp_password") or sour.get("source_sftp_password")
        if not request_info:
            # 模板化输入
            request_info["sftp_host"] = sour.get("sftp_host") or sour.get("source_sftp_host")
            request_info["sftp_user"] = sftp_user_list[sftp_user_index-1]
            request_info["sftp_password"] = sftp_password_list[sftp_user_index-1]
        return request_info
    def sftp_download_process(self, sour):
        request_info = self.prepare_sftp_request(sour)

        load_path = sour.get("file_load_from") or sour.get("source_load_file_from") or sour.get("load_file_from")
        out_path = sour.get("file_target_download_fpath") or sour.get("source_file_target_download_fpath")
        source_local_load_dir_cache = sour.get("file_local_load_dir_cache") or sour.get("source_local_load_dir_cache")
        file_download = sour.get("file_download")
        # 设置了缓存位置时优先缓存
        if source_local_load_dir_cache and file_download:
            out_path = source_local_load_dir_cache + file_download
        load_file_minsize = sour.get("file_load_minisize") or sour.get("source_load_file_minsize")

        sftp_program_process = SftpProcess(request_info, load_path, out_path, min_filesize=load_file_minsize,
                                           debug=self.debug)
        download_res = sftp_program_process.run()

        return download_res
        # if not load_res:
        #     print('%s load error' % load_path)
        #     return
        # if self.parser_c.ParseCustomize().final_parse(sour):
        #     self.parser_c(load_res, sour)
        # else:
        #     self.parse_normal_monitor(sour)

    def ftp_download_process(self, sour):
        request_info = sour.get("request_info", {})
        if not request_info:
            # 模板化输入
            request_info["ftp_ip"] = sour.get("source_ftp_ip")
            request_info["ftp_port"] = sour.get("source_ftp_port")
            request_info["ftp_user_id"] = sour.get("source_ftp_user_id")
            request_info["ftp_user_password"] = sour.get("source_ftp_user_password")

        file_download = sour.get("file_download")
        ftp_dir = sour.get("source_load_dir_from")
        out_path = sour.get("source_file_target_download_fpath")
        source_local_load_dir_cache = sour.get("source_local_load_dir_cache")
        # 设置了缓存位置时优先缓存
        if source_local_load_dir_cache and file_download:
            out_path = source_local_load_dir_cache + file_download

        ftp_program_process = FtpProcess(request_info, ftp_dir, file_download, out_path)
        download_res = ftp_program_process.run()
        # 这里同样可能出现对单一文件的处理
        # parse_customize.parse_customize_one
        return download_res
        # if not load_res:
        #     print('%s load error' % local_load_dir_cache)
        # return
        # if self.parser_c.ParseCustomize().final_parse(sour):
        #     self.parser_c.ParseCustomize().final_parse(sour)
        # else:
        #     self.parse_normal_monitor(load_res, sour)

    def api_process(self, url_source, parse_customize, request_type='api_get'):
        # 关于处理api流程，直观的期望处理给个url,直接进行抓取处理
        # 实际上的问题翻页问题，以及url中参数的问题，一般来说分为可控的参数，比如页数（自动累加）通过解析返回数据判断是否结束（包括返回的参数和传入限定的页数）
        # 再如不变的参数，可能的参数，每页数量
        page = setting.SOURCE_URL_START_PAGE
        pagesize = setting.SOURCE_URL_PAGESIZE
        url_stop_page_num = setting.SOURCE_URL_STOP_PAGE_NUM
        request_info = url_source.get("request_info", {})
        # source_request_load_file_path = url_source.get("source_request_load_file_path")
        error_count = 0
        need_next = True
        process_res = False
        url_params = {}
        if page:
            url_params["page"] = int(page)
        if pagesize:
            url_params["pagesize"] = int(pagesize)
        if url_stop_page_num:
            url_stop_page_num = int(url_stop_page_num)
        # url格式化模板规则定义
        # format key 可查找到 对应的key，参数字典查找，参数字典参数直接添加
        # 索引方式  定义,可读性不强？ 忽略可读性，直接参数序列?
        # url 拼接方式
        # 目的本质上是使用固定的模板组成可用的url供解析使用
        # 加入format key 找到key,部分key可变，例如page,或者其他code_num
        # 增加可控参数的输入，来覆盖。输入--》init_kwargs,k-v格式或可直接更改setting参数
        # 这一步是模板化参数，可以读取模板自动解析进行程序，完成简单的逻辑，这种有单一模板链接的项目
        # url 连接本质上可通过k-v 组合，有k,那么找对应的k-v字典集合，k-v 字典集合
        # 直接给url_params start_time->{PROJECT_DATE};end_time->{PROJECT_DATE}
        # cfg setting 的方式。。。。。目前是转换成对应的大写变量，不太合理，外部加入使用不易，若只是提供给内部调用，；整合成字典？变量名一致。。
        # 再封装个字典（ugly_code...)？存储所有对应的变量名和值
        #     url_params["url_stop_page_num"] = int(url_stop_page_num)
        #
        if self.debug:
            print('api_process,request_info:%s,url_param:%s' % (json.dumps(request_info), json.dumps(url_params)))
        while error_count < 10 and need_next:
            try:
                res_content = None
                url = url_source.get("url")
                if url_params:
                    url = url.format(**url_params)
                request_info["url"] = url
                if self.debug:
                    print(request_info)
                if request_type == 'api_get_file':
                    request_info["binary"] = True
                request_cli = RequestProcess(request_info, debug=self.debug)
                if request_type.startswith('api_get'):
                    res_content = request_cli.request_get_res()
                if not res_content:
                    error_count += 1
                    continue
                if request_type == 'api_get_file':
                    source_request_load_file_path = url_source.get("source_file_target_download_fpath")
                    if url_source.get("source_local_load_dir_cache") and url_source.get("file_download"):
                        source_request_load_file_path = url_source.get("source_local_load_dir_cache") + url_source.get(
                            "file_download")
                    if source_request_load_file_path:
                        try:
                            with open(source_request_load_file_path, 'wb') as f:
                                f.write(res_content)
                            process_res = True
                        except Exception as e:
                            traceback.print_exc()
                    else:
                        print('api_get_file no out_path!')
                    return process_res
                # parse_args = {res_content, page, pagesize}
                # 这里传入的参数，考虑动态化
                need_next = parse_customize.parse_customize_one(res_content, url_source, **url_params)
                if url_stop_page_num and url_params.get("page"):
                    if url_params.get("page") > url_stop_page_num:
                        break
                if need_next and url_params.get("page"):
                    url_params["page"] += 1
            except Exception as e:
                print('api_process error!')
                traceback.print_exc()
                error_count += 1
                time.sleep(10)

        return process_res
        # file_result = parse_customize.final_parse(url_source)
        # if url_source.get("pipeline_check_key") and not self.debug:
        #     self.parse_normal_monitor(file_result, url_source)

    def load_from_db_process(self, url_source, parse_customize, request_type):

        if request_type == 'mysql':
            self.load_from_mysql_process(url_source, parse_customize)
        elif request_type == 'redis':
            pass
        elif request_type == 'mssql':
            pass

    def load_from_mysql_process(self, url_source, parse_customize):
        from example_demo.utils.mysql_client import MysqlClient
        mysql_enable = url_source.get("mysql_enable")
        mysql_host = url_source.get("mysql_host")
        mysql_port = url_source.get("mysql_port")
        mysql_user = url_source.get("mysql_user")
        mysql_password = url_source.get("mysql_password")
        mysql_db_name = url_source.get("mysql_db_name")
        all_sqls = url_source.get("all_sqls_get")
        # mysql_sql = url_source.get("mysql_sql")
        # mysql_sql_param = url_source.get("mysql_sql_param")
        # mysqlclient 是使用MysqlDB,也可通过sqlalchemy，关于connect_url可拼接出来，缺点在于sql语句需要转义，编写不方便
        db_client = MysqlClient(mysql_host, mysql_user, mysql_password, mysql_db_name, port=mysql_port)


        for sql in all_sqls:
            result = db_client.connect_db_select(sql)
            if parse_customize.parse_customize_enable:
                parse_customize.parse_customize_one(result, url_source)


        # 多条语句的处理，sql 语句格式化的处理，可能需要保存
        # 关于语句的给用，load_sql,需也支持参数的传递
        # 通常的情况期望，这里只针对数据源获取（暂时不考虑多条的情况），只会有一个语句，但一般不会写固定的语句，存在参数的传递，写配置文件时项目初始的参数，以及之后的传参数据集，
        # 默认情况下，写一条语句，有两个参数需要传递,处理方式，传参上明了，call_tel -source_sql_param subject:wechat,receiver:zhangyf;wechatxxxxx


    def parse_normal_monitor(self, load_res, sour):
        '''
        通用化处理：邮件，解压，文件上报，删除缓存
        '''
        need_send_email = sour.get("email_enable")
        email_message = sour.get("email_message")
        if not email_message:
            email_subject = sour.get("email_subject", "")
            email_content = sour.get("email_content", "")
            email_message = (email_subject, email_content)

        tel_enable = sour.get("tel_enable")


        need_unzip = sour.get("need_unzip") or sour.get("file_need_unzip")
        unzip_path = sour.get("file_unzip_out_path") or sour.get("source_file_unzip_out_path")

        file_download = sour.get("file_download")
        source_local_load_dir_cache = sour.get("source_local_load_dir_cache")
        source_file_cache_copy_enable = sour.get("source_file_cache_copy_enable")
        source_file_cache_del_enable = sour.get("source_file_cache_del_enable")

        source_file_target_download_fpath = sour.get("file_target_download_fpath") or sour.get(
            "source_file_target_download_fpath")
        pipeline_fr_enable = sour.get("pipeline_fr_enable")
        pipeline_project_name = sour.get("pipeline_project_name")
        pipeline_check_key = sour.get("pipeline_check_key")
        pipeline_fr_fail = sour.get("pipeline_fr_fail")
        source_real_file_target_download_fpath = sour.get("source_real_file_target_download_fpath") if sour.get(
            "source_real_file_target_download_fpath") else source_file_target_download_fpath
        # 邮件
        if need_send_email:
            if self.debug:
                print(f'send_email:{email_message}')
                # return
            send_mail(*email_message)
        # 解压
        if unzip_path and load_res:
            try:
                common.un_zip(source_file_target_download_fpath, unzip_path)
            except Exception as e:
                print('un_zip_error')
                traceback.print_exc()
        # 缓存文件转存
        if source_file_cache_copy_enable and source_local_load_dir_cache and source_file_target_download_fpath and file_download:
            try:
                shutil.copy(source_local_load_dir_cache + file_download, source_file_target_download_fpath)
            except Exception as e:
                print('shutil.copy source_local_load_dir_cache error')
                traceback.print_exc()
        # 缓存文件删除
        if source_file_cache_del_enable and source_local_load_dir_cache and file_download:
            try:
                os.remove(source_local_load_dir_cache + file_download)
            except Exception as e:
                print('os.remove source_local_load_dir_cache error')
                traceback.print_exc()

        # pipeline file report
        if pipeline_fr_enable and pipeline_check_key and not self.debug:
            # file_path, download_date, project_name, pipline_path, check_key_head, debug=False
            # pipe_out_path = real_output_path if real_output_path else source_file_target_download_fpath

            if not load_res and pipeline_fr_fail:
                report_info = pipeline_check_key + '，检查不通过，文件' + source_real_file_target_download_fpath + ',不存在'
                pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, gs=False)
            elif load_res:
                file_size = str(os.path.getsize(source_file_target_download_fpath))
                report_info = pipeline_check_key + '，检查通过，文件' + source_real_file_target_download_fpath + ',已经存在'

                pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, debug=self.debug, gs=True,
                                  file_size=file_size)

    def parse_normal_monitor_ex(self, load_res, sour):
        source_file_target_download_fpath = sour.get("source_file_target_download_fpath")
        pipeline_project_name = sour.get("pipeline_project_name")
        pipeline_check_key = sour.get("pipeline_check_key")
        # local_file_path = sour.get("local_file_path")
        source_real_file_target_download_fpath = sour.get("source_real_file_target_download_fpath") if sour.get(
            "source_real_file_target_download_fpath") else source_file_target_download_fpath
        if not load_res:
            report_info = pipeline_check_key + '，检查不通过，文件' + source_real_file_target_download_fpath + ',不存在'
            pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, gs=False)
            return

        # shutil.copy(local_file_path, target_path)
        file_size = os.path.getsize(source_file_target_download_fpath)
        report_info = pipeline_check_key + '，检查通过，文件' + source_real_file_target_download_fpath + ',已经存在'

        pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, gs=True, file_size=file_size)

    def file_report_process(self, url_source, process_start=False):
        email_file_report = self.setting_info.get("email_file_report")
        email_content = ''
        project_name = self.setting_info.get("project_name")
        email_subject = f'{project_name} file_report'

        success_num = 0
        error_num = 0
        need_load_sour = []
        all_has = False
        for ind, sour in enumerate(url_source):
            source = copy.deepcopy(self.setting_info)
            source.update(sour)
            file_target_download_fpath = source.get("file_target_download_fpath") or source.get("source_file_target_download_fpath")
            real_file_target_download_fpath = source.get("file_real_target_download_fpath") or source.get("source_real_file_target_download_fpath")

            pipeline_check_key = source.get("pipeline_check_key")
            source_load_file_minsize = source.get("file_load_minsize") or source.get("source_load_file_minsize")
            message = ''

            download_in_db = source.get("download_in_db")
            if download_in_db:
                message = f'项目名称：{project_name}:更新数据库成功'
                success_num += 1
                print(message)
                continue

            if common.check_path(file_target_download_fpath, source_load_file_minsize):
                file_size = os.path.getsize(file_target_download_fpath)
                file_last_update_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime(os.stat(file_target_download_fpath).st_mtime))
                message = f'项目名称：{project_name}:{pipeline_check_key} -------------目标文件 check_success：{real_file_target_download_fpath},已存在，file_size：{file_size}, file_last_update_time:{file_last_update_time}'

                print(message)
                success_num += 1
            else:
                need_load_sour.append(source)
                if not process_start:
                    message = f'项目名称：{project_name}:{pipeline_check_key} -------------目标文件 check_error!：{real_file_target_download_fpath},不存在'
                    print(message)

                error_num += 1
            if message:
                email_content += message + '\r\n'
        all_file_num = success_num + error_num

        if process_start and len(need_load_sour) > 0:
            print(f'项目名称：{project_name},待下载目标文件总数：{len(need_load_sour)}')
        elif process_start and len(need_load_sour) == 0:
            print(f'项目名称：{project_name},was over.')

        else:
            print(f'项目名称：{project_name},目标文件总数：{all_file_num},has_success_num:{success_num},error_num:{error_num}')
            conclusion_txt = f'项目名称：{project_name},目标文件总数：{all_file_num},has_success_num:{success_num},error_num:{error_num}'
            email_content = conclusion_txt + '\r\n'
        if email_content and not process_start and email_file_report:
            send_mail(email_subject, email_content)
        if not need_load_sour:
            all_has = True
        return all_has, need_load_sour

    def handle(self):
        pass


class BaseProgram:
    pass
