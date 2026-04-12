from airflow.sdk import dag, task
from pathlib import Path
from datetime import datetime


@dag(
        dag_id="news_ingestion",
        start_date=datetime(2026, 4, 12),
        schedule="@daily",
        catchup=False
)
def news_ingestion() -> None:

    @task.python
    def fetch_feed_entries_and_save() -> Path:
        from ingestion import fetch_feed_entries
        return fetch_feed_entries()


    @task.python
    def upload_to_aws() -> str:
        from ingestion import upload_to_aws
        return upload_to_aws()
    
    @task.python
    def fetch_contents_and_save() -> Path:
        from ingestion import fetch_contents
        return fetch_contents()

    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_to_aws(feed_path)
    content_path = fetch_contents_and_save(aws_key)
    upload_to_aws(content_path)


news_ingestion()