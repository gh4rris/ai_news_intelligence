# from config import AWS_BUCKET

from airflow.sdk import dag, task
from pathlib import Path
from pendulum import datetime


# content_asset = Asset(f"s3://{AWS_BUCKET}/content")

@dag(
    dag_id="news_ingestion",
    start_date=datetime(year=2026, month=4, day=22, tz="Europe/London"),
    schedule=None,
    catchup=False
)
def news_ingestion() -> None:

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
    

    @task.bash
    def materialize_raw_and_cleansed_articles() -> str:
        return "cd /opt/airflow/ai_news_dbt && dbt run --select feed content articles"
    

    @task.bash
    def test_raw_and_cleansed_articles() -> str:
        return "cd /opt/airflow/ai_news_dbt && dbt test --select feed content articles"
    

    @task.python
    def article_enrichment_with_nlp():
        from nlp_processing import article_enrichment_with_nlp
        article_enrichment_with_nlp()

    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_feed_to_s3(feed_path)
    content_path = fetch_contents_and_save(aws_key)
    upload_content = upload_content_to_s3(content_path)
    materialize = materialize_raw_and_cleansed_articles()
    test = test_raw_and_cleansed_articles()
    enrichment = article_enrichment_with_nlp()
    

    upload_content >> materialize >> test >> enrichment


news_ingestion()