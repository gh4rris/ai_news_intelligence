from airflow.sdk import dag, task
from datetime import datetime


@dag(
        dag_id="news_ingestion_and_process",
        start_date=datetime(2026, 3, 5),
        schedule="@daily",
        catchup=False
)
def news_ingestion_and_process() -> None:

    @task.python
    def scrape_articles_and_load_to_database() -> None:
        from ingestion import scrape_articles_and_load_to_database
        scrape_articles_and_load_to_database()


    @task.python
    def process_articles_and_load_to_database() -> None:
        from nlp_processing import process_articles_and_load_to_database
        process_articles_and_load_to_database()

    
    scrape = scrape_articles_and_load_to_database()
    process = process_articles_and_load_to_database()

    scrape >> process


news_ingestion_and_process()