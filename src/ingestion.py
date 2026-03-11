from config import RSS_FEED, MAX_CONCURRENT, REQUEST_TIMEOUT
from utils import run_async
from models import RawDataModel
from schemas.raw_data import RawData
from database import Session

import hashlib
import asyncio
from asyncio import Semaphore
import aiohttp
from aiohttp import ClientSession
import trafilatura
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
import feedparser as fp
from feedparser import FeedParserDict
from datetime import datetime


@run_async
async def scrape_articles_and_load_to_database():
    feed_entries = fetch_feed_entries()
    contents = await fetch_contents(feed_entries)
    articles = validate_and_filter_data(feed_entries, contents)
    load_articles_to_database(articles)


def fetch_feed_entries() -> list[FeedParserDict]:
    feed_entries = []

    for source_name, source_url in RSS_FEED.items():
        feed = fp.parse(source_url)
        feed_urls = [entry.get("link", "") for entry in feed["entries"]]
        existing_urls = get_existing_urls(feed_urls)
        new_entries = [entry for entry in feed["entries"] if entry.get("link") not in existing_urls]

        for entry in new_entries:
            entry["source"] = source_name
        feed_entries.extend(new_entries)

    return feed_entries


def get_existing_urls(urls: list[str]) -> set[str]:
    with Session() as session:
        statement = sa.select(RawDataModel.url).where(RawDataModel.url.in_(urls))
        result = session.execute(statement).scalars().all()
        
    return set(result)


async def fetch_contents(feed_entries: list[FeedParserDict]) -> list[str | None]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for article_url in [entry.get("link", "") for entry in feed_entries]:
            task = asyncio.create_task(fetch_article_content(session, semaphore, article_url))
            tasks.append(task)
        return await asyncio.gather(*tasks)
    

async def fetch_article_content(session: ClientSession, semaphore: Semaphore, url: str) -> str | None:
    async with semaphore:
        try:
            async with session.get(url, timeout=REQUEST_TIMEOUT) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
        except Exception:
            return None
        
        return trafilatura.extract(html)


def validate_and_filter_data(feed_entries: list[FeedParserDict], contents: list[str | None]) -> list[RawData]:
    articles: list[RawData] = []
    
    ingestion_timestamp = datetime.now()
    for entry, content in zip(feed_entries, contents):
        article_url = entry.get("link")
        if article_url:
            article = RawData(
                article_id=generate_article_id(article_url),
                title=entry.get("title"),
                url=article_url,
                source_name=entry.get("source"),
                author=entry.get("author"),
                summary=entry.get("description"),
                published_at=parse_date(entry),
                ingested_at=ingestion_timestamp,
                content=content
            )
        articles.append(article)

    articles = [article for article in articles if article.content and len(article.content) > 200]

    return articles


def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def parse_date(article: FeedParserDict) -> datetime | None:
    if article.get("published_parsed"):
        return datetime(*article["published_parsed"][:6])
    return None


def load_articles_to_database(articles: list[RawData]) -> None:
    with Session() as session:
        statement = insert(RawDataModel).values([article.model_dump() for article in articles])
        statement = statement.on_conflict_do_nothing(index_elements=["url"])
        session.execute(statement)
        session.commit()