from config import DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_ACCESS_TOKEN

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
        access_token=DATABRICKS_ACCESS_TOKEN
    )

def db_query(query: str, params: list=[]) -> DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        result: Table = cur.fetchall_arrow()
        return result.to_pandas()
