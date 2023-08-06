import pandas as pd
from sqlalchemy import create_engine
import example_demo.setting as setting


class SqlDbClient():
    def __init__(self, vendordb1_connect_url='',):
        vendordb1_connect_url = vendordb1_connect_url or setting.MSSQLDB_CONNECT_URL
        self.engine = create_engine(vendordb1_connect_url)

    def read_sql(self, sql):
        return pd.read_sql_query(sql, con=self.engine)

    def to_sql(self, df, table_name='', if_exists='append', index=False):
        # table_name = table_name or
        table_name = table_name or setting.MSSQLDB_TABLE
        df.to_sql(table_name, self.engine, if_exists=if_exists, index=index)
