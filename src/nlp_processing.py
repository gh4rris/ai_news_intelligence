from config import SENTIMENT_MODEL, ENTITY_EXTRACTOR_MODEL, TOPIC_KEYWORDS
from models import RawArticleModel, NLPArticleModel
from schemas.nlp_article import NLPArticle
from database import SessionLocal

import logging
import sqlalchemy as sa
import spacy
from datetime import datetime
from transformers import pipeline


logger = logging.getLogger(__name__)
sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL)
nlp = spacy.load(ENTITY_EXTRACTOR_MODEL)


def process_articles_and_load_to_database() -> None:
    unprocessed_articles = get_unprocessed_articles()
    logger.info(f"{len(unprocessed_articles)} unprocessed articles retrieved")
    articles = []

    for article_id, content in unprocessed_articles:
        sentiment, score = get_sentiment(content)
        topics = classify_topics(content)
        entities = extract_entities(content)

        article = NLPArticle(
            article_id=article_id,
            sentiment=sentiment,
            sentiment_score=score,
            topics=topics,
            entities=entities,
            processed_at=datetime.now()
        )
        articles.append(article)
    logger.info(f"{len(articles)} articles processed")

    load_processed_articles_to_database(articles)
    logger.info(f"{len(articles)} processed articles loaded to database")


def get_unprocessed_articles() -> list[tuple[str, str]]:
    statement = sa.select(
        RawArticleModel.article_id,
        RawArticleModel.content
        ).outerjoin(NLPArticleModel).where(NLPArticleModel.article_id.is_(None))
    
    with SessionLocal() as session:
        rows = session.execute(statement).fetchall()

    return [tuple(row) for row in rows]


def get_sentiment(text: str) -> tuple[str, float]:
    result = sentiment_pipeline(text[:512])[0]
    return result["label"], result["score"]


def classify_topics(text: str) -> list[str]:
    topics = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text.lower() for keyword in keywords):
            topics.append(topic)

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


def load_processed_articles_to_database(articles: list[NLPArticle]) -> None:
    with SessionLocal() as session:
        statement = sa.insert(NLPArticleModel).values([article.model_dump() for article in articles])
        session.execute(statement)
        session.commit()