from airflow.sdk import dag, task
from pathlib import Path
from pendulum import datetime


@dag(
    dag_id="ingestion_dag",
    start_date=datetime(year=2026, month=6, day=16, tz="Europe/London"),
    schedule=None,
    catchup=False
)
def ingestion_dag() -> None:

    @task.python
    def fetch_feed_entries_and_save() -> str:
        from ingestion import fetch_feed_entries
        path = fetch_feed_entries()
        return str(path)


    @task.python
    def upload_feed_to_s3(path: str) -> str:
        from ingestion import upload_to_s3
        return upload_to_s3(Path(path))
    

    @task.python
    def fetch_contents_and_save(key: str) -> str:
        from ingestion import fetch_contents
        path = fetch_contents(key)
        return str(path)
    

    @task.python()
    def upload_content_to_s3(path: str) -> str:
        from ingestion import upload_to_s3
        return upload_to_s3(Path(path))
    
    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_feed_to_s3(feed_path)
    content_path = fetch_contents_and_save(aws_key)
    upload_content_to_s3(content_path)


ingestion_dag()