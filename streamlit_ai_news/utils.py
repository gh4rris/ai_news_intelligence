from config import DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET

import streamlit as st
from databricks import sql
from databricks.sql.client import Connection
from pandas import DataFrame
from pyarrow import Table


@st.cache_resource
def get_connection() -> Connection:
    return sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_HTTP_PATH,
        client_id=DATABRICKS_CLIENT_ID,
        client_secret=DATABRICKS_CLIENT_SECRET
    )

def db_query(query: str, params: list=[]) -> DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        result: Table = cur.fetchall_arrow()
        return result.to_pandas()
