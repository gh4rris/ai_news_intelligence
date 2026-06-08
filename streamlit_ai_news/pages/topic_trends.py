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


def display(df: DataFrame) -> None:
    st.dataframe(df)
    fig = px.scatter(
        df, x="published_date", y="topic", size="article_count",
        color="dominant_sentiment", title="Topic Volume and Sentiment Over Time",
        color_discrete_map={"POSITIVE": "green", "NEGATIVE": "red"}
    )
    st.plotly_chart(fig)


col1, col2 = st.columns(2)

from_date = col1.date_input("From", value=datetime.today() - timedelta(days=30))
to_date = col2.date_input("To", value=datetime.today())

if st.button("Submit"):
    df = get_topics_between(from_date, to_date)
    display(df)
