# from ingestion_dag import content_asset

from airflow.sdk import dag, task


# @dag(
#     dag_id="nlp_processing",
#     schedule=[content_asset]
# )
# def nlp_processing() -> None:

#     @task.bash(inlets=[content_asset])
#     def materialize_raw_and_cleansed_articles() -> str:
#         return "cd /opt/airflow/ai_news_dbt && dbt run --select feed content articles"
    

#     @task.bash
#     def test_raw_and_cleansed_articles() -> str:
#         return "cd /opt/airflow/ai_news_dbt && dbt test --select feed content articles"
    

#     @task.python
#     def article_enrichment_with_nlp():
#         from nlp_processing import article_enrichment_with_nlp
#         article_enrichment_with_nlp()

#     materialize = materialize_raw_and_cleansed_articles()
#     test = test_raw_and_cleansed_articles()
#     enrichment = article_enrichment_with_nlp()

#     materialize >> test >> enrichment


# nlp_processing()