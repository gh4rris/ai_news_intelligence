from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
import plotly.express as px
from datetime import datetime, date
from pandas import DataFrame


st.set_page_config(
    page_title="Daily Summary"
)

st.title("Daily Summary")


def get_summary_data(selected_date: date) -> DataFrame:
    return db_query(f"""
    SELECT *
    FROM {DATABRICKS_CATALOG}.gold.daily_summary
    WHERE published_date = ?
    ORDER BY published_date
    """, [selected_date])


def display(df: DataFrame, selected_date: date) -> None:
    daily_metrics = df.iloc[0]
    container.subheader(f"Daily metrics: {selected_date.strftime("%d/%m/%Y")}")
    col1.metric("Total Articles", daily_metrics["total_articles"])
    col2.metric("Most Active Source", daily_metrics["most_active_source"])
    col1.metric("Percentage Positive", f"{daily_metrics["pct_positive"]}%")
    col2.metric("Percentage Negative", f"{daily_metrics["pct_negative"]}%")
    col1.metric("Top Topic", daily_metrics["top_topic"])
    col2.metric("Top Entity", f"{daily_metrics["top_entity_label"]}: {daily_metrics["top_entity_text"]}",)
    fig = px.bar(df, x="published_date", y=["pct_positive", "pct_negative"],
                 title="Daily Sentiment Breakdown",
                 color_discrete_map={
                 "pct_positive": "green",
                 "pct_negative": "red"
                 })
    st.plotly_chart(fig)


selected_date = st.date_input("Select a date", value=datetime.today())
submit = st.button("Submit")
container = st.container()
col1, col2 = st.columns(2)


if submit:
    df = get_summary_data(selected_date)

    if len(df) >= 1:
        display(df, selected_date)
    else:
        container.subheader(f"No articles for {selected_date.strftime("%d/%m/%Y")}")

