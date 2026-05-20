from config import DBT_PATH, DBT_IMAGE, DBT_WORK_DIR, DOCKER_URL

from airflow.sdk import dag, task
from pathlib import Path
from pendulum import datetime
from docker.types import Mount


@dag(
    dag_id="ai_news",
    start_date=datetime(year=2026, month=4, day=28, tz="Europe/London"),
    schedule=None,
    catchup=False
)
def ai_news() -> None:

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
    

    @task.docker(
        image=DBT_IMAGE,
        docker_url=DOCKER_URL,
        network_mode="bridge",
        mounts=[
            Mount(
                source=DBT_PATH,
                target=DBT_WORK_DIR,
                type="bind"
            )
        ],
        auto_remove="success"
    )
    def materialize_raw_and_cleansed_articles() -> int:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "dbt", "run", "--select", "feed", "content", "articles"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(result.stderr)
        return result.returncode
    

    @task.python
    def article_enrichment_with_nlp() -> None:
        from nlp_processing import article_enrichment_with_nlp
        article_enrichment_with_nlp()
    
    
    @task.docker(
        image=DBT_IMAGE,
        docker_url=DOCKER_URL,
        network_mode="bridge",
        mounts=[
            Mount(
                source=DBT_PATH,
                target=DBT_WORK_DIR,
                type="bind"
            )
        ],
        auto_remove="success"
    )
    def transform_intermediate_and_gold() -> int:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "dbt", "run", "--select", "intermediate", "gold"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(result.stderr)
        return result.returncode


    @task.docker(
        image=DBT_IMAGE,
        docker_url=DOCKER_URL,
        network_mode="bridge",
        mounts=[
            Mount(
                source=DBT_PATH,
                target=DBT_WORK_DIR,
                type="bind"
            )
        ],
        auto_remove="success"
    )
    def test_all_tables() -> int:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "dbt", "test"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(result.stderr)
        return result.returncode

    
    feed_path = fetch_feed_entries_and_save()
    aws_key = upload_feed_to_s3(feed_path)
    content_path = fetch_contents_and_save(aws_key)
    upload_content = upload_content_to_s3(content_path)
    raw_and_cleansed = materialize_raw_and_cleansed_articles()
    enrichment = article_enrichment_with_nlp()
    intermediate_and_gold = transform_intermediate_and_gold()
    test_tables = test_all_tables()
    

    upload_content >> raw_and_cleansed >> enrichment >> intermediate_and_gold >> test_tables


ai_news()