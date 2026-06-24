from config import AWS_BUCKET, DBT_PATH, DBT_IMAGE, DBT_WORK_DIR, DOCKER_URL

from airflow.sdk import dag, task
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from pendulum import datetime
from docker.types import Mount


@dag(
    dag_id="nlp_dag",
    start_date=datetime(year=2026, month=6, day=16, tz="Europe/London"),
    schedule=None,
    catchup=False
)
def nlp_dag() -> None:

    check_for_parquet = S3KeySensor(
        task_id="check_for_new_parquet",
        bucket_name=AWS_BUCKET,
        bucket_key="content/{{ ds }}_content.parquet",
        aws_conn_id="aws",
        mode="reschedule",
        poke_interval=10,
        timeout=120,
        soft_fail=False
    )

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

    
    raw_and_cleansed = materialize_raw_and_cleansed_articles()
    enrichment = article_enrichment_with_nlp()
    intermediate_and_gold = transform_intermediate_and_gold()
    test_tables = test_all_tables()
    

    check_for_parquet >> raw_and_cleansed >> enrichment >> intermediate_and_gold >> test_tables


nlp_dag()
