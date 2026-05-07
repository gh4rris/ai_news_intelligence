from ai_news_streamlit.config import DATABRICKS_CATALOG
from ai_news_streamlit.utils import db_query

import streamlit as st
from datetime import datetime


st.set_page_config(
    page_title="Main Page",
    layout="centered"
)

st.title("Main Page")

selected_date = st.date_input("Date", value=datetime.today())

df = db_query(f"""
SELECT *
FROM {DATABRICKS_CATALOG}.gold.daily_summary
WHERE published_date = ?
ORDER BY published_date
""", [selected_date])

st.dataframe(df)
