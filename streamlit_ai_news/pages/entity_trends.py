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
st.subheader("Track organization, people and product mentions")


def get_day_entities(selected_date: date, entity_type: str, min_mentions: int) -> DataFrame:
    return db_query(f"""
    SELECT *
    FROM {DATABRICKS_CATALOG}.gold.entity_trends
    WHERE published_date = ?
    AND (entity_label = ? OR ? = 'ALL')
    AND mention_count >= ?
    ORDER BY mention_count ASC
    """, [selected_date, entity_type, entity_type, min_mentions])


def get_entities_beetween(from_date: date, to_date: date, entity_type: str, min_mentions: int) -> DataFrame:
    return db_query(f"""
    WITH grouped AS
    (
        SELECT entity_label, entity_text, SUM(mention_count) AS total_mention_count
        FROM {DATABRICKS_CATALOG}.gold.entity_trends
        GROUP BY entity_label, entity_text
    )

    SELECT et.published_date, et.entity_label, et.entity_text, et.mention_count, et.dominant_sentiment, g.total_mention_count
    FROM {DATABRICKS_CATALOG}.gold.entity_trends AS et
    INNER JOIN grouped AS g
    ON et.entity_label = g.entity_label AND et.entity_text = g.entity_text
    WHERE published_date BETWEEN ? AND ?
    AND (et.entity_label = ? OR ? = 'ALL')
    AND total_mention_count >= ?
    ORDER BY total_mention_count ASC
    """, [from_date, to_date, entity_type, entity_type, min_mentions])


def bar_display(df: DataFrame, title: str) -> None:
    fig = px.bar(df,
                 x="mention_count", y="entity_text",
                 orientation="h", color="dominant_sentiment",
                 color_discrete_map={
                    "POSITIVE": "green",
                    "NEGATIVE": "red"
                 },
                 title=title)
    st.plotly_chart(fig)


def line_display(df: DataFrame, title: str) -> None:
    fig = px.line(df, x="published_date", y="mention_count",
                  color="entity_text", title=title)
    st.plotly_chart(fig)


col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
submit_button = st.button("Submit")

entity_type = col1.selectbox("Entity type", ["ORG", "PERSON", "PRODUCT", "ALL"])
min_mentions = col2.slider("Min mentions", 1, 50, 5)

date_format = col1.radio("Date", ["Day", "Between"], horizontal=True)

match entity_type:
    case "ORG":
        type_string = "Organsation "
    case "PERSON":
        type_string = "Person "
    case "PRODUCT":
        type_string = "Product "
    case "ALL":
        type_string = ""

if date_format == "Day":
    selected_date = col3.date_input("Date", datetime.today())

    if submit_button:
        title = f"Most Mentioned {type_string} Entities: {selected_date.strftime("%d/%m/%Y")} (min {min_mentions})"
        df = get_day_entities(selected_date, entity_type, min_mentions)
        bar_display(df, title)

if date_format == "Between":
    from_date = col3.date_input("From", datetime.today() - timedelta(days=30))
    to_date = col4.date_input("To", datetime.today())

    if submit_button:
        bar_title = f"Total {type_string}Entity Mentions Between {from_date.strftime("%d/%m/%Y")} and {to_date.strftime("%d/%m/%Y")} (period min {min_mentions})"
        line_title = f"Daily {type_string}Entity Mentions Between {from_date.strftime("%d/%m/%Y")} and {to_date.strftime("%d/%m/%Y")} (period min {min_mentions})"
        df = get_entities_beetween(from_date, to_date, entity_type, min_mentions)
        bar_display(df, bar_title)
        line_display(df, line_title)

