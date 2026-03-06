from airflow.sdk import DAG, task
from datetime import datetime

@task
def fetch_articles():
    from src.ingestion import fetch_articles
    fetch_articles()

@task
def deduplicate_articles():
    from src.ingestion import deduplicate_articles
    deduplicate_articles()

with DAG(
    dag_id="news_ingestion",
    start_date=datetime(2026, 3, 5),
    schedule="@daily",
    catchup=False
) as dag:
    
    fetch = fetch_articles()
    deduplicate = deduplicate_articles()

    fetch >> deduplicate