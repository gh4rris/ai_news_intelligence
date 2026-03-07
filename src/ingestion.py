from src.models.raw_data import Base, RawData
from src.config import RSS_FEED, DB_URL

import hashlib
import requests
import trafilatura
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import feedparser as fp
from feedparser import FeedParserDict
from datetime import datetime


def fetch_articles() -> list[RawData]:
    articles = []

    for source_name, url in RSS_FEED.items():
        feed = fp.parse(url)
        ingestion_timestamp = datetime.now()
        
        for entry in feed["entries"]:
            article_url = entry.get("link")
            if article_url:
                article = RawData(
                    article_id=generate_article_id(article_url),
                    title=entry.get("title"),
                    url=article_url,
                    source_name=source_name,
                    author=entry.get("author"),
                    summary=entry.get("summary"),
                    published_at=parse_date(entry),
                    ingested_at=ingestion_timestamp,
                    content=fetch_article_content(article_url)
                )
            articles.append(article)

    return articles


def fetch_article_content(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        return None
    
    return trafilatura.extract(response.text)


def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def parse_date(entry: FeedParserDict) -> datetime | None:
    if entry.get("published_parsed"):
        return datetime(*entry["published_parsed"][:6])
    return None


def load_articles_to_database(articles: list[RawData]) -> None:
    db = sa.create_engine(DB_URL)
    Session = sessionmaker(bind=db)
    Base.metadata.create_all(db)

    with Session() as session:
        for article in articles:
            session.add(article)
            session.commit()