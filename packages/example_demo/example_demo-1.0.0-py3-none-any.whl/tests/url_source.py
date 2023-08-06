# -*- coding: utf-8 -*-
import os
from example_demo.commons.common_fun import check_path
import datetime

path_test = r'C:\\Users\\zhangyf\\Downloads\\demo_load\\'

request_type = 'sftp'

sftp_host = 'sftp-preview.barra.com'
sftp_port = 22
# 改成同一个账号
sftp_user = 'ovolluxw'
sftp_password = 'musL9Lol9pes#Bz9PZ+f'
sftp_user_ase2 = 'ovolluxw'
sftp_user_password_ase2 = 'musL9Lol9pes#Bz9PZ+f'

ase2_output_dir = r'\\172.30.16.20\z\vendor\msci\barra\ASE2S\update\\'
ase2_unzip_path = r'\\172.30.16.20\z\vendor\msci\barra\ASE2S\update\daily\\'


class UrlSource:

    def __init__(self, now_date='', debug=False, **kwargs):
        self.now_date = now_date if now_date else (datetime.date.today() - datetime.timedelta(days=1)).strftime(
            '%Y%m%d')
        self.current_year = self.now_date[:4]
        self.download_date = self.now_date[2:]
        self.debug = debug

        # self.request_info = {"host": self.host, "user": self.user, "connect_kwargs": {'password': self.password}}

    def load_barra_ase2(self):

        file1 = "GMD_ASE2_LOCALID_ID_%s.zip"
        file2 = "GMD_ASE2_Market_Data_%s.zip"
        file3 = "GMD_ASE2S_100_%s.zip"
        file4 = "GMD_ASE2S_100_ETF_%s.zip"
        file5 = "GMD_ASE2S_100_UnadjCov_%s.zip"
        file6 = "GMD_ASE2_100_Std_Descriptor_%s.zip"
        all_files = [file1, file2, file3, file4, file5, file6]
        all_files = [file % self.download_date for file in all_files]

        output_dir = os.path.join(ase2_output_dir, self.current_year)
        # load_info = [{"load_path": "/ase2/" + file, "out_path": os.path.join(output_dir, file)} for file in all_files]
        # file1 file3 file6 需要unzip ,其他的不需要 ?
        need_unzip_files_index = [0, 2, 5]
        load_info = []
        if self.debug:
            output_dir = path_test
        for file_index, file in enumerate(all_files):
            out_path = os.path.join(output_dir, file)
            if check_path(out_path):
                continue
            info = {}
            info["file"] = file
            info["sftp_load_path"] = "/ase2/" + file
            info["sftp_out_path"] = out_path
            info["request_info"] = {"sftp_host": sftp_host, "sftp_user": sftp_user_ase2,
                                    "sftp_password": sftp_user_password_ase2}
            info["need_unzip"] = True if file_index in need_unzip_files_index else False
            info["unzip_path"] = ase2_unzip_path
            info["need_send_email"] = True if file_index in need_unzip_files_index else False
            load_info.append(info)

        return load_info

    def load_all_source(self):
        barra_eutr = self.load_barra_ase2()

        return barra_eutr

    def get_request_type(self):
        return request_type


if __name__ == '__main__':
    res = UrlSource().load_barra_ase2()
    print(res)