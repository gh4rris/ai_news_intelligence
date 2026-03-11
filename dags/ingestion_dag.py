from airflow.sdk import DAG, task
from datetime import datetime


@task
def scrape_articles_and_load_to_database() -> None:
    from ingestion import scrape_articles_and_load_to_database
    scrape_articles_and_load_to_database()


with DAG(
    dag_id="news_ingestion",
    start_date=datetime(2026, 3, 5),
    schedule="@daily",
    catchup=False
) as dag:
    
    scrape_articles_and_load_to_database()