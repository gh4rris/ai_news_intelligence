import streamlit as st
from databricks import sql
from databricks.sql.client import Connection
from databricks.sdk.core import Config, oauth_service_principal, OAuthCredentialsProvider
from pandas import DataFrame
from pyarrow import Table


def credential_provider() -> OAuthCredentialsProvider:
    return oauth_service_principal(
        Config(
            host=f"https://{st.secrets["host"]}",
            client_id=st.secrets["client_id"],
            client_secret=st.secrets["client_secret"]
        )
    )

@st.cache_resource
def get_connection() -> Connection:
    return sql.connect(
        server_hostname=st.secrets["host"],
        http_path=st.secrets["http_path"],
        credentials_provider=credential_provider
    )

# @st.cache_data(ttl=3600)
def db_query(query: str, params: list=[]) -> DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        result: Table = cur.fetchall_arrow()
        return result.to_pandas()
