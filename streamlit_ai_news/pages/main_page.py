from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
import plotly.express as px
from datetime import datetime


st.set_page_config(
    page_title="Main Page",
    layout="centered"
)

st.title("Daily Summary")

selected_date = st.date_input("Select a date", value=datetime.today())
st.subheader(f"Daily metrics: {selected_date.strftime("%d/%m/%Y")}")

df = db_query(f"""
SELECT *
FROM {DATABRICKS_CATALOG}.gold.daily_summary
WHERE published_date = ?
ORDER BY published_date
""", [selected_date])

col1, col2 = st.columns(2)

daily_metrics = df[df.published_date == selected_date]


if len(daily_metrics) >= 1:
    daily_metrics = daily_metrics.iloc[0]
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