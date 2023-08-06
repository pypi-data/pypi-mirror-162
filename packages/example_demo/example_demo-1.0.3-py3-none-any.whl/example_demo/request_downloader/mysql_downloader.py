from typing import Any, List, Optional, Tuple, Dict
import datetime
import MySQLdb
import example_demo.setting as setting
# from example_demo.setting import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB_NAME
from example_demo.exceptions import OnedatautilConfigException
from example_demo.request_downloader.download_base import BaseHook


class MysqlHook(BaseHook):
    """

    """

    default_request_info = {}
    request_type = 'mysql'
    hook_name = 'MYSQL'

    def __init__(self, request_info: dict, run_path='') -> None:
        super().__init__()
        self.request_info = request_info
        # self.sql = sql
        # self.sql_get_all = sql_get_all
        self.conn: Optional[MySQLdb.connect] = None
        if run_path:
            setting.reload_setting(run_path)
    def __enter__(self):
        return self

    def get_conn(self) -> MySQLdb.connect:
        """"""

        conn_config = self.get_connection()
        return MySQLdb.connect(**conn_config)

    def get_connection(self) -> Dict:
        if not self.request_info:
            if not setting.MYSQL_DB_NAME or not setting.MYSQL_HOST or not setting.MYSQL_PORT or not setting.MYSQL_USER or not setting.MYSQL_PASSWORD:
                raise OnedatautilConfigException(f"MYsql download no cfg")
            #
            self.request_info = dict(
                host=setting.MYSQL_HOST,
                port=setting.MYSQL_PORT,
                user=setting.MYSQL_USER,
                passwd=setting.MYSQL_PASSWORD,
                schema=setting.MYSQL_DB_NAME,
            )
        conn_config = {
            'user': self.request_info.get("user"),
            'password': self.request_info.get("passwd") or '',
            'host': self.request_info.get("host") or 'localhost',
            'database': self.request_info.get("schema") or '',
            'port': self.request_info.get("port") if self.request_info.get("port") else 3306,
        }
        return conn_config

    def sql_get(self, sql, all_get=True):
        r = []
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            r = cursor.execute(sql)
            r = cursor.fetchone() if not all_get else cursor.fetchall()
            cursor.close()
            conn.commit()
            conn.close()
        except Exception as e:
            print('db_sql_get error')
        return r


class MYSQLDownloader(MysqlHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour

        request_info = self.sour.get("request_info")

        kwargs['request_info'] = request_info
        # sql_get = self.sour.get("sql_get")
        # sql_get_all = self.sour.get("sql_get_all", False)
        # kwargs['sql'] = sql_get
        # kwargs['sql_get_all'] = sql_get_all

        super().__init__(*args, **kwargs)

    def download(self):
        sql_get = self.sour.get("mysql_sql_get")
        sql_get_all = self.sour.get("mysql_get_all", False)
        download_res = False
        retry_nums = 3
        get_res = []
        # if self.remote_exist(remote_path):
        for i in range(retry_nums):
            try:
                get_res = self.sql_get(sql_get, sql_get_all)
                download_res = True
                break
            except:
                print(f'sql_get:{sql_get}, mysql download error,try_num:{i}')
                continue
                # raise OnedatautilConfigException(f'path:{remote_path}, download error')
        # else:
        #     print(f'no such path:{remote_path}')
        # raise OnedatautilConfigException(f'no such path:{remote_path}')
        return download_res, get_res
