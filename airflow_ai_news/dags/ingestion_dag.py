from airflow.sdk import dag, task
from airflow.models.xcom_arg import XComArg
from pathlib import Path
from pendulum import datetime
from typing import cast


@dag(
    dag_id="ingestion_dag",
    start_date=datetime(year=2026, month=7, day=1, tz="Europe/London"),
    schedule="@daily",
    catchup=False
)
def ingestion_dag() -> None:

    @task.python
    def fetch_feed_entries_and_save() -> str:
        from ingestion import fetch_feed_entries
        path = fetch_feed_entries()
        return str(path)


    @task.python
    def upload_feed_to_s3(path: XComArg) -> str:
        from ingestion import upload_to_s3
        return upload_to_s3(Path(cast(str, path)))
    

    @task.python
    def fetch_contents_and_save(key: XComArg) -> str:
        from ingestion import fetch_contents
        key_str = cast(str, key)
        path = fetch_contents(key_str)
        return str(path)
    

    @task.python()
    def upload_content_to_s3(path: XComArg) -> str:
        from ingestion import upload_to_s3
        return upload_to_s3(Path(cast(str, path)))
    
    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_feed_to_s3(feed_path) 
    content_path = fetch_contents_and_save(aws_key)
    upload_content_to_s3(content_path)


ingestion_dag()
