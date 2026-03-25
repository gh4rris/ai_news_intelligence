from airflow.sdk import DAG, task
from datetime import datetime


@task
def scrape_articles_and_load_to_database() -> None:
    from ingestion import scrape_articles_and_load_to_database
    scrape_articles_and_load_to_database()


@task
def process_articles_and_load_to_database() -> None:
    from nlp_processing import process_articles_and_load_to_database
    process_articles_and_load_to_database()


with DAG(
    dag_id="news_ingestion_and_process",
    start_date=datetime(2026, 3, 5),
    schedule="@daily",
    catchup=False
) as dag:
    
    scrape = scrape_articles_and_load_to_database()
    process = process_articles_and_load_to_database()

    scrape >> process