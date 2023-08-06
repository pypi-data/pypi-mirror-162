import pandas as pd
from sqlalchemy import create_engine

vendordb1_connect_url = r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
engine = create_engine(vendordb1_connect_url)
query_sql = ""
df = pd.read_sql_query(query_sql, con=engine)

# df.to_sql(table_name, engine, if_exists='append', index=False)



def db_sql():
    pass