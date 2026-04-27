from config import SENTIMENT_MODEL

import logging
import pendulum
from transformers import pipeline
from databricks.sql.types import Row
from airflow.providers.databricks.hooks.databricks_sql import DatabricksSqlHook


logger = logging.getLogger(__name__)
sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL)
# nlp = spacy.load(ENTITY_EXTRACTOR_MODEL)


def article_enrichment_with_nlp() -> None:
    hook = DatabricksSqlHook(databricks_conn_id="databricks")
    articles = fetch_todays_scraped_content(hook)
    logger.info(f"Articles fetched: {len(articles)}")
    enriched_articles = []
    for article in articles:
        sentiment, score = get_sentiment(article.content)
        processed_timestamp = pendulum.now()
        enriched_articles.append(
            (
                article.article_id,
                sentiment,
                score,
                processed_timestamp
            )
        )
    create_if_not_exists_sentiment(hook)
    insert_into_sentiment(hook, enriched_articles)
    logger.info("Data inserted")


def fetch_todays_scraped_content(hook: DatabricksSqlHook) -> list[Row]:
    return hook.get_records("""
    SELECT article_id, content
    FROM ai_news.silver.articles
    WHERE CAST(content_ingestion AS DATE) = CURRENT_DATE
    """)


def create_if_not_exists_sentiment(hook: DatabricksSqlHook) -> None:
    hook.run("""
    CREATE TABLE IF NOT EXISTS ai_news.silver.sentiment (
    article_id STRING,
    sentiment STRING,
    score DOUBLE,
    processed_at TIMESTAMP
    )
    """)


def insert_into_sentiment(hook: DatabricksSqlHook, sentiments: list[tuple]) -> None:
    values = ", ".join(
        f"('{article_id}', '{sentiment}', {score}, '{processed_timestamp}')"
        for article_id, sentiment, score, processed_timestamp in sentiments
        )
    hook.run(f"""
    INSERT INTO ai_news.silver.sentiment (article_id, sentiment, score, processed_at)
    VALUES {values}
    """)


# def process_articles_and_load_to_database() -> None:
#     unprocessed_articles = get_unprocessed_articles()
#     logger.info(f"{len(unprocessed_articles)} unprocessed articles retrieved")
#     articles = []

#     for article_id, content in unprocessed_articles:
#         sentiment, score = get_sentiment(content)
#         topics = classify_topics(content)
#         entities = extract_entities(content)

#         article = NLPArticle(
#             article_id=article_id,
#             sentiment=sentiment,
#             sentiment_score=score,
#             topics=topics,
#             entities=entities,
#             processed_at=datetime.now()
#         )
#         articles.append(article)
#     logger.info(f"{len(articles)} articles processed")

#     load_processed_articles_to_database(articles)
#     logger.info(f"{len(articles)} processed articles loaded to database")


# def get_unprocessed_articles() -> list[tuple[str, str]]:
#     statement = sa.select(
#         RawArticleModel.article_id,
#         RawArticleModel.content
#         ).outerjoin(NLPArticleModel).where(NLPArticleModel.article_id.is_(None))
    
#     with SessionLocal() as session:
#         rows = session.execute(statement).fetchall()

#     return [tuple(row) for row in rows]


def get_sentiment(text: str) -> tuple[str, float]:
    result = sentiment_pipeline(text[:512])[0]
    return result["label"], round(result["score"], 2)


# def classify_topics(text: str) -> list[str]:
#     topics = []

#     for topic, keywords in TOPIC_KEYWORDS.items():
#         if any(keyword in text.lower() for keyword in keywords):
#             topics.append(topic)

#     return topics or ["Other"]


# def extract_entities(text: str) -> list[dict[str, str]]:
#     doc = nlp(text)
#     entities = [
#         {
#             "label": entity.label_,
#             "text": entity.text
#         }
#         for entity in doc.ents
#     ]
#     return entities


# def load_processed_articles_to_database(articles: list[NLPArticle]) -> None:
#     with SessionLocal() as session:
#         statement = sa.insert(NLPArticleModel).values([article.model_dump() for article in articles])
#         session.execute(statement)
#         session.commit()