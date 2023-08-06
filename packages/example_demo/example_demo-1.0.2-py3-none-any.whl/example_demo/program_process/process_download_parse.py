import os
import traceback
from os.path import abspath
from inspect import getsourcefile
from example_demo.request_downloader.ftp_downloader import FTPDownloader
from example_demo.request_downloader.sftp_downloader import SFTPDownloader
from example_demo.request_downloader.mysql_downloader import MYSQLDownloader
from example_demo.request_downloader.http_downloader import HTTPDownloader
import example_demo.commons.common_fun as common


class DownloadParse():
    def __init__(self, source, parser, *args, **kwargs):
        # import example_demo.setting as setting
        self.request_type = source.get("request_type")

        self.source = source

        self.parser = parser
        run_path = os.getcwd()
        parser_path = os.path.dirname(abspath(getsourcefile(parser)))
        self.run_path = ''
        if run_path != parser_path:
            print(f'reload:{parser_path}')
            # setting.reload_setting(parser_path)
            self.run_path = parser_path
        # self.setting = setting

    def __enter__(self):
        return self

    def main_process(self):

        parse_customize = self.parser.ParseCustomize()
        download_res, get_res = False, []

        if self.request_type in ("sftp", "ftp"):
            download_res = self.download_direct()
        elif self.request_type.startswith('api'):
            download_res = self.http_process(parse_customize)
        elif self.request_type in ('mysql', 'redis', 'mssql'):
            download_res, get_res = self.load_from_db_process(parse_customize)
        if not download_res:
            return

    def download_direct(self):
        '''
        直接下载文件落地的抓取（ftp,sftp,request请求后转存文件的方式）
        通常落地
        （若有）对文件的自定义的处理(parse_one)
        常规收尾处理（缓存copy & del,文件上报，邮件发送)
        '''
        download_hook = None
        if self.request_type == 'sftp':
            download_hook = SFTPDownloader(self.source, run_path=self.run_path)

        elif self.request_type == 'ftp':
            download_hook = FTPDownloader(self.source, run_path=self.run_path)
            # 这里同样可能出现对单一文件的处理
        # if parse_customize.parse_customize_one
        download_res = download_hook.download()

        return download_res

    def load_from_db_process(self, parse_customize):
        download_res, get_res = False, []
        if self.request_type == 'mysql':
            download_res, get_res = MYSQLDownloader(self.source).download()
        elif self.request_type == 'redis':
            pass
        elif self.request_type == 'mssql':
            pass
        if parse_customize.parse_customize_enable and get_res:
            parse_customize.parse_customize_one(get_res, self.source)
        if parse_customize.final_parse_enable:
            parse_customize.final_parse(self.source)

        return download_res, get_res

    def http_process(self, parse_customize):
        # 翻页的情况,初始页数,判断到尾页的逻辑:has_stop_page(默认)
        data_params = self.source.get("url_params")
        page_scan = False
        page_key = ''
        process_res = True
        if data_params:
            for k, param in data_params.items():
                if param == '{page}':
                    page_scan = True
                    page_key = k
        if page_scan:
            self.http_page_process(page_key, parse_customize)
        else:
            download_res, res_content = HTTPDownloader(self.source).downloader()
            if parse_customize.parse_customize_enable and res_content:
                parse_customize.parse_customize_one(res_content, self.source)
        return process_res

    #  size->{source_url_pagesize};page->{page};start_time->{source_date};end_time->{source_date};
    def http_page_process(self, page_key, parse_customize):
        # (('size',page_size),('page',page),('start_time','20220719'),('end_rime','20220719'))
        request_url_start_page = self.source.get("request_url_start_page") or 1

        request_url_stop_page = self.source.get("request_url_stop_page")

        data_params = self.source.get("url_params")
        data_params[page_key] = request_url_start_page
        # 未指定截止页数时,可通过自定义,
        # if not request_url_stop_page:
        #     pass
        # else:
        while True:
            download_res, res_content = HTTPDownloader(self.source).downloader()

            need_next = parse_customize.parse_customize_one(res_content, self.source, page=data_params.get(page_key))

            if not need_next or (request_url_stop_page and data_params.get(page_key) > request_url_stop_page):
                break
            data_params[page_key] += 1

        if parse_customize.final_parse_enable:
            parse_customize.final_parse(self.source)


def parse_normal_monitor(self, load_res):
        '''
        通用化处理：邮件，解压，文件上报，删除缓存
        '''
        # need_send_email = self.source.get("email_enable")
        # email_message = self.source.get("email_message")
        # if not email_message:
        #     email_subject = self.source.get("email_subject", "")
        #     email_content = self.source.get("email_content", "")
        #     email_message = (email_subject, email_content)
        #
        # tel_enable = self.source.get("tel_enable")

        need_unzip = self.source.get("need_unzip") or self.source.get("file_need_unzip")
        unzip_path = self.source.get("file_unzip_out_path") or self.source.get("source_file_unzip_out_path")

        file_download = self.source.get("file_download")
        source_local_load_dir_cache = self.source.get("source_local_load_dir_cache")
        source_file_cache_copy_enable = self.source.source.get("source_file_cache_copy_enable")
        source_file_cache_del_enable = self.source.get("source_file_cache_del_enable")

        source_file_target_download_fpath = self.source.get("local_filepath")
        pipeline_fr_enable = self.source.get("pipeline_fr_enable")
        pipeline_project_name = self.source.get("pipeline_project_name")
        pipeline_check_key = self.source.get("pipeline_check_key")
        pipeline_fr_fail = self.source.get("pipeline_fr_fail")
        source_real_file_target_download_fpath = self.source.get(
            "source_real_file_target_download_fpath") if self.source.get(
            "source_real_file_target_download_fpath") else source_file_target_download_fpath
        # 邮件
        # if need_send_email:
        #     if self.debug:
        #         print(f'send_email:{email_message}')
        #         # return
        #     send_mail(*email_message)
        # 解压
        if unzip_path and load_res:
            try:
                common.un_zip(source_file_target_download_fpath, unzip_path)
            except Exception as e:
                print('un_zip_error')
                traceback.print_exc()
        # 缓存文件转存
        # if source_file_cache_copy_enable and source_local_load_dir_cache and source_file_target_download_fpath and file_download:
        #     try:
        #         shutil.copy(source_local_load_dir_cache + file_download, source_file_target_download_fpath)
        #     except Exception as e:
        #         print('shutil.copy source_local_load_dir_cache error')
        #         traceback.print_exc()
        # 缓存文件删除
        # if source_file_cache_del_enable and source_local_load_dir_cache and file_download:
        #     try:
        #         os.remove(source_local_load_dir_cache + file_download)
        #     except Exception as e:
        #         print('os.remove source_local_load_dir_cache error')
        #         traceback.print_exc()

        # pipeline file report
        # if pipeline_fr_enable and pipeline_check_key and not self.debug:
        #     # file_path, download_date, project_name, pipline_path, check_key_head, debug=False
        #     # pipe_out_path = real_output_path if real_output_path else source_file_target_download_fpath
        #
        #     if not load_res and pipeline_fr_fail:
        #         report_info = pipeline_check_key + '，检查不通过，文件' + source_real_file_target_download_fpath + ',不存在'
        #         pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, gs=False)
        #     elif load_res:
        #         file_size = str(os.path.getsize(source_file_target_download_fpath))
        #         report_info = pipeline_check_key + '，检查通过，文件' + source_real_file_target_download_fpath + ',已经存在'
        #
        #         pipe_monitor_file(pipeline_project_name, pipeline_check_key, report_info, debug=self.debug, gs=True,
        #                           file_size=file_size)
