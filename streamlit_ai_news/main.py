from config import DAILY_SUMMARY, TOPIC_TRENDS, ENTITY_TRENDS, DATA_EXPLORATION, SOURCE_PROFILES

import streamlit as st


def main():
    daily_summary = st.Page(DAILY_SUMMARY, title="Daily Summary")
    topic_trends = st.Page(TOPIC_TRENDS, title="Topic Trends")
    entity_trends = st.Page(ENTITY_TRENDS, title="Entity Trends")
    source_profiles = st.Page(SOURCE_PROFILES, title="Source Profiles")
    data_exploration = st.Page(DATA_EXPLORATION, title="Data Exploration")

    pages = st.navigation([daily_summary, topic_trends, entity_trends, data_exploration, source_profiles])

    pages.run()


if __name__ == "__main__":
    main()
