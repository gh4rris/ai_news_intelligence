from src.ingestion import fetch_articles, load_articles_to_database

from airflow.sdk import DAG, task
from datetime import datetime

@task
def fetch_and_store_articles():
    articles = fetch_articles()

    if articles:
        load_articles_to_database(articles)


with DAG(
    dag_id="news_ingestion",
    start_date=datetime(2026, 3, 5),
    schedule="@daily",
    catchup=False
) as dag:
    
    fetch_and_store_articles()