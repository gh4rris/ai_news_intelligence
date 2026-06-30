from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta, date
from pandas import DataFrame


st.set_page_config(
    page_title="Source Profiles"
)

st.title("Source Profiles")
st.subheader("Analysing article sources")

def get_sources_between(from_date: date, to_date: date) -> DataFrame:
    return db_query(f"""
    SELECT *
    FROM {DATABRICKS_CATALOG}.gold.source_profiles
    WHERE published_date BETWEEN ? AND ?
    ORDER BY published_date
    """, [from_date, to_date])


def display(df: DataFrame, from_date: str, to_date: str) -> None:
    fig = px.bar(
        df, x="source", y="article_count", color="dominant_dentiment",
        title=f"Article Count by Source and Sentiment between {from_date} and {to_date}"
    )
    st.plotly_chart(fig)


col1, col2 = st.columns(2)

from_date = col1.date_input("From", value=datetime.today() - timedelta(days=30))
to_date = col2.date_input("To", value=datetime.today())

if st.button("Submit"):
    sources_df = get_sources_between(from_date, to_date)
    display(sources_df, from_date.strftime("%d/%m/%Y"), to_date.strftime("%d/%m/%Y"))
