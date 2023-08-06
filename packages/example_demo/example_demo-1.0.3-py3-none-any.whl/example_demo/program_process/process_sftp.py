# -*- coding: utf-8 -*-
import traceback
import time
from example_demo.request_downloader.downloaders import sftp_farbic_connect
import example_demo.commons.common_fun as common
import datetime
import os

class SftpProcess():
    def __init__(self, request_info, load_path, out_path, load_need_email=False, email_message=[], need_unzip=False,
                 unzip_path='',
                 need_monitor_file=False, download_date='', min_filesize=0, debug=False, **kwargs):
        self.request_info = request_info
        self.load_path = load_path
        self.out_path = out_path
        self.need_unzip = need_unzip
        self.unzip_path = unzip_path
        self.load_need_email = load_need_email
        self.email_message = email_message
        self.need_monitor_file = need_monitor_file
        self.download_date = download_date if download_date else (
                    datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        self.min_filesize = min_filesize
        self.debug = debug

    def get_connect(self):
        return sftp_farbic_connect(**self.request_info)

    def sftp_download(self, sftp_con):
        load_res = False
        for i in range(3):
            try:
                if self.debug:
                    print('---------start_load:%s-----------' % self.load_path)
                    print(f'load_path:{self.load_path},out_path:{self.out_path}')
                sftp_con.get(self.load_path, self.out_path)
                if common.check_path(self.out_path, self.min_filesize):
                    load_res = True
                    file_size = os.path.getsize(self.out_path)

                    print(f'load_success! {self.out_path},size:{file_size}')
                    break
            except Exception as e:
                traceback.print_exc()
                time.sleep(2)
                continue
        return load_res

    def run(self):

        sftp_con = sftp_farbic_connect(**self.request_info)
        load_res = self.sftp_download(sftp_con)
        if self.debug:
            print(f'download_over ,load_path:{self.load_path},out_path:{self.out_path},load_res:{load_res}')

        return load_res
        # if not load_res:
        #     if self.debug:
        #         print('load_error')
        #     return False
        # if self.load_need_email:
        #     if self.debug:
        #         print('send_email')
        #     # to_list "[172.30.16.31]msci barra ase2 message"   download_date + " done."
        #     send_mail(*self.email_message)
        #
        # if self.need_unzip and self.unzip_path:
        #     try:
        #         un_zip(self.out_path, self.unzip_path)
        #     except Exception as e:
        #         print('un_zip_error')
        #         traceback.print_exc()
        # if self.need_monitor_file:
        #     if self.debug:
        #         print('pipe_monitor_file')
            # pipe_monitor_file(self.out_path, self.download_date)
