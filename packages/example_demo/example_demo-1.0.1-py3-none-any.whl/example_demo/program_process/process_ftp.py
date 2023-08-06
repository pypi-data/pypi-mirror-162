# -*- coding: utf-8 -*-
import traceback
import time
from example_demo.request_downloader.downloaders import ftp_connect
import example_demo.commons.common_fun as common
import datetime


class FtpProcess():
    def __init__(self, request_info, ftp_dir, download_file_name, local_file_path,  debug=False, **kwargs):
        self.request_info = request_info
        self.ftp_dir = ftp_dir
        self.download_file_name = download_file_name
        self.local_file_path = local_file_path
        self.debug = debug

    def cwd_load_file(self, ftp_con):
        load_res = False
        try:
            ftp_con.cwd(self.ftp_dir)
            buf_size = 1024  # 设置的缓冲区大小
            ftp_file_list = ftp_con.nlst()
            if self.download_file_name in ftp_file_list:
                file_obj = open(self.local_file_path, "wb")
                file_handle = file_obj.write  # 以写模式在本地打开文件
                ftp_con.retrbinary("RETR %s" % self.download_file_name, file_handle, buf_size)  # 接收服务器上文件并写入本地文件
                # ftp.set_debuglevel(0)  # 关闭调试模式
                # print(f'{download_file_name} download finished.')
                file_obj.close()
                ftp_con.quit()  # 退出ftp
                load_res = True
        except Exception as e:
            traceback.print_exc()
            time.sleep(2)
        return load_res
    def run(self):
        ftp_con = ftp_connect(**self.request_info)
        load_res = self.cwd_load_file(ftp_con)

        return load_res