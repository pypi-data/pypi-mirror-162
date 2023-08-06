# -*- coding: UTF-8 -*-
from request_downloader.downloaders import *
from commons.common_fun import check_path, un_zip
import os
import jd_py_base
def request_downloader_check_file(request_info, request_type, load_path, out_path, min_size, need_unzip=False, unzip_path=''):
    if check_path(out_path, check_file_size=True, min_size=min_size):
        return
    connect = None
    if request_type == 'sftp':
        connect = sftp_farbic_connect(**request_info)

    # elif request_type == 'ftp':
    #     connect = ftp_connect(**request_info)

    load_res = False
    for i in range(3):
        try:
            connect.get(load_path, out_path)
            if check_path(out_path, check_file_size=True, min_size=min_size):
                load_res = True
                break
        except Exception as e:
            traceback.print_exc()
            time.sleep(2)
            continue
    if load_res and need_unzip and unzip_path:
        try:
            un_zip(out_path, unzip_path)
        except Exception as e:
            print('un_zip_error')
            traceback.print_exc()
            os.remove(out_path)
print(dir(jd_py_base))