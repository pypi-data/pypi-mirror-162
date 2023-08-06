import MySQLdb
from dbutils.pooled_db import PooledDB, SharedDBConnection


class MysqlClient:
    def __init__(self, host, user, password, db, port=3306):
        self.pool = PooledDB(MySQLdb,
                             mincached=30,
                             host=host,
                             user=user,
                             passwd=password,
                             db=db,
                             port=port,
                             charset='utf8')

    def connect_db_select(self, sql, all_get=False):
        r = []
        try:
            con = self.pool.connection()
            cur = con.cursor()
            r = cur.execute(sql)
            r = cur.fetchone() if not all_get else cur.fetchall()
            con.commit()
            cur.close()
            con.close()
        except Exception as e:
            print('connect_db_select error')
        return r
