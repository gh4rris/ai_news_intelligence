from config import SENTIMENT_MODEL, ENTITY_EXTRACTOR_MODEL, DATABRICKS_CATALOG, TOPIC_KEYWORDS, KEYWORD_THRESHOLD, HF_TOKEN

import logging
import pendulum
import re
import json
import spacy
from transformers import pipeline
from databricks.sql.types import Row
from databricks import sql
from airflow.providers.databricks.hooks.databricks_sql import DatabricksSqlHook


logger = logging.getLogger(__name__)
sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL, token=HF_TOKEN)
nlp = spacy.load(ENTITY_EXTRACTOR_MODEL)


def article_enrichment_with_nlp() -> None:
    hook = DatabricksSqlHook(databricks_conn_id="databricks")
    articles = fetch_todays_scraped_content(hook)
    logger.info(f"Articles fetched: {len(articles)}")

    nlp_results = []
    for article in articles:
        sentiment, score = get_sentiment(article.content)
        topics = classify_topics(article.content)
        entities = extract_entities(article.content)
        processed_timestamp = pendulum.now()
        nlp_results.append(
            (
                article.article_id,
                sentiment,
                score,
                json.dumps(topics),
                json.dumps(entities),
                processed_timestamp
            )
        )
    create_table_if_not_exists(hook)
    insert_into_nlp_articles(hook, nlp_results)
    logger.info(f"Records inserted: {len(nlp_results)}")


def fetch_todays_scraped_content(hook: DatabricksSqlHook) -> list[Row]:
    return hook.get_records(f"""
    SELECT article_id, content
    FROM {DATABRICKS_CATALOG}.silver.articles
    WHERE CAST(content_ingestion AS DATE) = CURRENT_DATE
    """)


def create_table_if_not_exists(hook: DatabricksSqlHook) -> None:
    hook.run(f"""
    CREATE TABLE IF NOT EXISTS {DATABRICKS_CATALOG}.silver.nlp_articles (
    article_id STRING,
    sentiment STRING,
    sentiment_score DOUBLE,
    topics ARRAY<STRING>,
    entities ARRAY<MAP<STRING, STRING>>,
    processed_at TIMESTAMP
    )
    """)


def insert_into_nlp_articles(hook: DatabricksSqlHook, values: list[tuple]) -> None:
    with sql.connect(
        server_hostname=hook.host,
        http_path=hook._http_path,
        access_token=hook._token
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany(f"""
            INSERT INTO {DATABRICKS_CATALOG}.silver.nlp_articles (article_id, sentiment, sentiment_score, topics, entities, processed_at)
            VALUES (?, ?, ?, from_json(?, 'array<string>'), from_json(?, 'array<map<string,string>>'), ?)
            """, values)


def get_sentiment(text: str) -> tuple[str, float]:
    result = sentiment_pipeline(text[:512])[0]
    return result["label"], round(result["score"], 2)


def classify_topics(text: str) -> list[str]:
    article_lower = text.lower()
    scores = {
        topic: sum(
            len(re.findall(rf"\b{keyword}\b", article_lower))
            for keyword in keywords
        )
        for topic, keywords in TOPIC_KEYWORDS.items()
    }

    topics = [
        topic
        for topic, score in scores.items()
        if score >= KEYWORD_THRESHOLD
    ]

    return topics or ["Other"]


def extract_entities(text: str) -> list[dict[str, str]]:
    doc = nlp(text)
    entities = [
        {
            "label": entity.label_,
            "text": entity.text
        }
        for entity in doc.ents
    ]
    return entities
