from src.models.raw_data import Base, RawData
from src.config import RSS_FEED, MAX_CONCURRENT, DB_URL
from src.utils import run_async

import hashlib
import asyncio
from asyncio import Semaphore
import aiohttp
from aiohttp import ClientSession
import trafilatura
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import feedparser as fp
from feedparser import FeedParserDict
from datetime import datetime


@run_async
async def fetch_articles() -> list[RawData]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    articles = []

    for source_name, source_url in RSS_FEED.items():
        feed = fp.parse(source_url)
        ingestion_timestamp = datetime.now()

        async with aiohttp.ClientSession() as session:
            tasks = []
            for article_url in [article.get("link") for article in feed["entries"]]:
                task = asyncio.create_task(fetch_article_content(session, semaphore, article_url))
                tasks.append(task)
            contents = await asyncio.gather(*tasks)
        
        for article, content in zip(feed["entries"], contents):
            article_url = article.get("link")
            if article_url:
                article = RawData(
                    article_id=generate_article_id(article_url),
                    title=article.get("title"),
                    url=article_url,
                    source_name=source_name,
                    author=article.get("author"),
                    summary=article.get("description"),
                    published_at=parse_date(article),
                    ingested_at=ingestion_timestamp,
                    content=content
                )
            articles.append(article)

    return articles


async def fetch_article_content(session: ClientSession, semaphore: Semaphore, url: str) -> str | None:
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
        except Exception:
            return None
        
        return trafilatura.extract(html)


def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def parse_date(article: FeedParserDict) -> datetime | None:
    if article.get("published_parsed"):
        return datetime(*article["published_parsed"][:6])
    return None


def load_articles_to_database(articles: list[RawData]) -> None:
    db = sa.create_engine(DB_URL)
    Session = sessionmaker(bind=db)
    Base.metadata.create_all(db)

    with Session() as session:
        for article in articles:
            session.add(article)
            session.commit()