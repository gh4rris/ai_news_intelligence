from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
from datetime import datetime, timedelta, date
from pandas import DataFrame


st.set_page_config(
    page_title="Data Exploration"
)

st.title("Data Exploration")
st.subheader("Filter and search the article database")


def get_filtered_day(source: str, selected_date: date, keyphrase: str) -> DataFrame:
    return db_query(f"""
    SELECT title, link, author, published, summary, source
    FROM {DATABRICKS_CATALOG}.silver.articles
    WHERE (source = ? OR 'All' = ?)
    AND published = ?
    AND (title ILIKE ? OR summary ILIKE ?)
    """, [source, source, selected_date, keyphrase, keyphrase])


def get_filtered_between(source: str, from_date: date, to_date: date, keyphrase: str) -> DataFrame:
    return db_query(f"""
    SELECT title, link, author, published, summary, source
    FROM {DATABRICKS_CATALOG}.silver.articles
    WHERE (source = ? OR 'All' = ?)
    AND published BETWEEN ? AND ?
    AND (title ILIKE ? OR summary ILIKE ?)
    """, [source, source, from_date, to_date, keyphrase, keyphrase])


col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
submit_button = st.button("Submit")

source = col1.selectbox("Select Source", ["All", "TechCrunch", "The Verge", "Wired", "MIT Technology Review"])
keyphrase = col1.text_input("Keyphrase")
keyphrase = f"%{keyphrase}%"
date_format = col1.radio("Date", ["Day", "Between"], horizontal=True)

if date_format == "Day":
    selected_date = col3.date_input("Date", datetime.today())

    if submit_button:
        df = get_filtered_day(source, selected_date, keyphrase)
        st.dataframe(df)

if date_format == "Between":
    from_date = col3.date_input("From", datetime.today() - timedelta(days=30))
    to_date = col4.date_input("To", datetime.today())

    if submit_button:
        df = get_filtered_between(source, from_date, to_date, keyphrase)
        st.dataframe(df)
