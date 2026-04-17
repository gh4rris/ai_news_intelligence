from airflow.sdk import dag, task
from pathlib import Path
from pendulum import datetime



@dag(
        dag_id="news_ingestion",
        start_date=datetime(year=2026, month=4, day=17, tz="Europe/London"),
        schedule="@daily",
        catchup=False
)
def news_ingestion() -> None:

    @task.python
    def fetch_feed_entries_and_save() -> str:
        from ingestion import fetch_feed_entries
        path = fetch_feed_entries()
        return str(path)


    @task.python
    def upload_to_aws(path: str) -> str:
        from ingestion import upload_to_aws
        return upload_to_aws(Path(path))
    

    @task.python
    def fetch_contents_and_save(key: str) -> str:
        from ingestion import fetch_contents
        path = fetch_contents(key)
        return str(path)
    

    @task.bash
    def run_dbt_bronze_and_silver() -> str:
        return "cd /opt/airflow/ai_news_dbt && dbt run"
    

    @task.bash
    def dbt_test_bronze_and_silver() -> str:
        return "cd /opt/airflow/ai_news_dbt && dbt test"

    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_to_aws(feed_path)
    content_path = fetch_contents_and_save(aws_key)
    upload_content_to_s3 = upload_to_aws(content_path)
    create_bronze_and_silver_layer = run_dbt_bronze_and_silver()
    test_bronze_and_silver_layer = dbt_test_bronze_and_silver()

    upload_content_to_s3 >> create_bronze_and_silver_layer >> test_bronze_and_silver_layer


news_ingestion()