from typing import Any, List, Optional, Tuple
import datetime
import fabric

import example_demo.setting as setting
# from example_demo.setting import SFTP_HOST, SFTP_USER, SFTP_PORT, SFTP_PASSWORD
from example_demo.exceptions import OnedatautilConfigException
from example_demo.request_downloader.download_base import BaseHook


class SFTPHook(BaseHook):
    """

    """

    default_request_info = {}
    request_type = 'sftp'
    hook_name = 'SFTP'

    def __init__(self, request_info: dict, user_index: int, run_path='') -> None:
        super().__init__()
        self.request_info = request_info
        self.user_index = user_index
        self.conn: Optional[fabric.Connection] = None
        # self.setting_info = setting_info
        if run_path:
            setting.reload_setting(run_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.conn is not None:
            self.close_conn()

    def get_conn(self) -> fabric.Connection:
        """Returns a SFTP connection object"""
        if self.conn is None:
            request_info = self.get_connection()
            self.conn = fabric.Connection(host=request_info.get("host"), user=request_info.get("user"), connect_kwargs={'password': request_info.get("passwd")},
                                         connect_timeout=request_info.get("connect_timeout"))

        return self.conn

    def get_connection(self):
        if not self.request_info:
            if not setting.SFTP_HOST or not setting.SFTP_PORT or not setting.SFTP_USER or not setting.SFTP_PASSWORD:
                raise OnedatautilConfigException(f"sftp download no cfg")
            sftp_user = setting.SFTP_USER
            sftp_pwd = setting.SFTP_PASSWORD

            if isinstance(setting.SFTP_USER, list):
                sftp_user = setting.SFTP_USER[self.user_index]
            if isinstance(setting.SFTP_PASSWORD, list):
                sftp_pwd = setting.SFTP_PASSWORD[self.user_index]
            self.request_info = dict(
                host=setting.SFTP_HOST,
                user=sftp_user,
                passwd=sftp_pwd,
                connect_timeout=10
            )
        return self.request_info

    def close_conn(self):
        """
        Closes the connection. An error will occur if the
        connection wasn't ever opened.
        """
        conn = self.conn
        conn.close()
        self.conn = None

    def remote_exist(self, file_path):

        """

        判断远端文件是否存在

        :return: 布尔值

        """
        con = self.get_conn()


        if int(con.run(" [ -e " + file_path + " ] && echo 11 || echo 10")) == 11:
            return True
        else:
            return False


class SFTPDownloader(SFTPHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour
        request_info = self.sour.get("request_info")

        kwargs['request_info'] = request_info
        kwargs["user_index"] = sour.get("user_index") if sour.get("user_index") else 0

        super().__init__(*args, **kwargs)

    def download(self):
        con = self.get_conn()
        remote_path = self.sour.get("remote_path")
        local_filepath = self.sour.get("local_filepath")
        download_res = False
        retry_nums = 3
        # if self.remote_exist(remote_path):
        for i in range(retry_nums):
            try:
                con.get(remote_path, local_filepath)
                download_res = True
                break
            except Exception as e:
                print(f'path:{remote_path}, sftp download error:{e},try_num:{i}')
                continue
                # raise OnedatautilConfigException(f'path:{remote_path}, download error')
        # else:
        #     print(f'no such path:{remote_path}')
            # raise OnedatautilConfigException(f'no such path:{remote_path}')
        return download_res
