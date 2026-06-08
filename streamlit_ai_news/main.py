from config import DAILY_SUMMARY, TOPIC_TRENDS, ENTITY_TRENDS

import streamlit as st


def main():
    daily_summary = st.Page(DAILY_SUMMARY, title="Daily Summary")
    topic_trends = st.Page(TOPIC_TRENDS, title="Topic Trends")
    entity_trends = st.Page(ENTITY_TRENDS, title="Entity Trends")

    pages = st.navigation([daily_summary, topic_trends, entity_trends])

    pages.run()


if __name__ == "__main__":
    main()