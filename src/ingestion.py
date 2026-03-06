from models.raw_data import RawData
from config import RSS_FEED

import hashlib
import requests
import trafilatura
import feedparser as fp
from feedparser import FeedParserDict
from datetime import datetime


def fetch_articles():
    articles: list[RawData] = []

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
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None
    
    return trafilatura.extract(response.text)


def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def parse_date(entry: FeedParserDict) -> datetime | None:
    if entry.get("published_parsed"):
        return datetime(*entry["published_parsed"][:6])
    return None


def deduplicate_articles():
    print("Deduplicating articles...")