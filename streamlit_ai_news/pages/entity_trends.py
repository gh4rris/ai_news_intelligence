from config import DATABRICKS_CATALOG
from utils import db_query

import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta, date
from pandas import DataFrame


st.set_page_config(
    page_title="Entity Trends"
)

st.title("Entity Trends")

def get_day_entities(selected_date: date, entity_type: str, min_mentions: int) -> DataFrame:
    return db_query(f"""
    SELECT *
    FROM {DATABRICKS_CATALOG}.gold.entity_trends
    WHERE published_date = ?
    AND (entity_label = ? OR ? = 'ALL')
    AND mention_count >= ?
    ORDER BY mention_count DESC
    """, [selected_date, entity_type, entity_type, min_mentions])


def get_entities_beetween(from_date: date, to_date: date, entity_type: str, min_mentions: int) -> DataFrame:
    return db_query(f"""
    SELECT *

    FROM {DATABRICKS_CATALOG}.gold.entity_trends
    WHERE published_date BETWEEN ? AND ?
    AND (entity_label = ? OR ? = 'ALL')
    AND mention_count >= ?
    ORDER BY mention_count DESC
    """, [from_date, to_date, entity_type, entity_type, min_mentions])


def display(df: DataFrame, title: str) -> None:
    st.dataframe(df)
    fig = px.bar(df.sort_values("mention_count", ascending=True),
                 x="mention_count",
                 y="entity_text",
                 orientation="h",
                 color="dominant_sentiment",
                 color_discrete_map={
                    "POSITIVE": "green",
                 "NEGATIVE": "red"
                 },
                 title=title)
    st.plotly_chart(fig)


col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
submit_button = st.button("Submit")

entity_type = col1.selectbox("Entity type", ["ORG", "PERSON", "PRODUCT", "ALL"])
min_mentions = col2.slider("Min mentions", 1, 50, 5)

date_format = col1.radio("Date", ["Day", "Between"], horizontal=True)


if date_format == "Day":
    selected_date = col3.date_input("Date", datetime.today())
    if submit_button:
        title = f"Most Mentioned Entities: {selected_date.strftime("%d/%m/%Y")}"
        df = get_day_entities(selected_date, entity_type, min_mentions)
        display(df, title)
if date_format == "Between":
    from_date = col3.date_input("From", datetime.today() - timedelta(days=30))
    to_date = col4.date_input("To", datetime.today())
    if submit_button:
        title = f"Most Mentioned Entities Between {from_date.strftime("%d/%m/%Y")} and {to_date.strftime("%d/%m/%Y")}"
        df = get_entities_beetween(from_date, to_date, entity_type, min_mentions)
        display(df, title)

