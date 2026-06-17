from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta, date
from pandas import DataFrame


st.set_page_config(
    page_title="Topic Trends"
)

st.title("Topic Trends")


def get_topics_between(from_date: date, to_date: date) -> DataFrame:
    return db_query(f"""
    SELECT *
    FROM {DATABRICKS_CATALOG}.gold.topic_trends
    WHERE published_date BETWEEN ? AND ?
    ORDER BY published_date
    """, [from_date, to_date])


def display(df: DataFrame, from_date: str, to_date: str) -> None:
    fig1 = px.line(
        df, x="published_date", y="article_count", color="topic",
        title=f"Article count by topic between {from_date} and {to_date}"
    )
    fig2 = px.bar(
        df, x="topic", y="article_count", color="dominant_sentiment",
        title=f"Total Article count by topic and dominant sentiment between {from_date} and {to_date}",
        color_discrete_map={"POSITIVE": "green", "NEGATIVE": "red"}
    )
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)


col1, col2 = st.columns(2)

from_date = col1.date_input("From", value=datetime.today() - timedelta(days=30))
to_date = col2.date_input("To", value=datetime.today())

if st.button("Submit"):
    topics_df = get_topics_between(from_date, to_date)
    display(topics_df, from_date.strftime("%d/%m/%Y"), to_date.strftime("%d/%m/%Y"))
