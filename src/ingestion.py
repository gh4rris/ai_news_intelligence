from config import RSS_FEED, MAX_CONCURRENT, REQUEST_TIMEOUT, FEED_PATH, CONTENT_PATH, AWS_BUCKET
from utils import run_async

import logging
import hashlib
import asyncio
import json
import boto3
from pathlib import Path
from asyncio import Semaphore
import aiohttp
from aiohttp import ClientSession
import trafilatura
import pandas as pd
import feedparser as fp
from feedparser import FeedParserDict
import pendulum
from pendulum import DateTime, datetime


logger = logging.getLogger(__name__)


def fetch_feed_entries() -> Path:
    total_feed_entries = []
    ingestion_timestamp = pendulum.now()
    
    for source_name, source_url in RSS_FEED.items():
        feed = fp.parse(source_url)
        feed_entries = [
            {
                "article_id": generate_article_id(entry.get("link", "")),
                **entry,
                "title_detail": json.dumps(entry.get("title_detail", {})),
                "links": json.dumps(entry.get("links", [])),
                "authors": json.dumps(entry.get("authors", [])),
                "published_parsed": parse_date(entry),
                "tags": json.dumps(entry.get("tags", [])),
                "summary_detail": json.dumps(entry.get("summary_detail", {})),
                "source": source_name,
                "ingested_at": ingestion_timestamp
            } for entry in feed["entries"]
        ]
        
        total_feed_entries.extend(feed_entries)
    
    logger.info(f"RSS feed scrapped at: {ingestion_timestamp.strftime("%d/%m/%Y %H:%M:%S")}")
    return save_to_parquet(total_feed_entries, ingestion_timestamp, FEED_PATH)


def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def parse_date(article: FeedParserDict) -> DateTime | None:
    if article.get("published_parsed"):
        return datetime(*article["published_parsed"][:6])
    return None


def save_to_parquet(data: list[dict], ingested_at: DateTime, path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    date = ingested_at.strftime("%Y-%m-%d")
    file_path = path / f"{date}_{path.name}.parquet"
    df.to_parquet(file_path, engine="pyarrow", coerce_timestamps="us", index=False, compression="zstd")

    logger.info(f"{file_path.name} saved to path: {file_path}")
    return file_path


def upload_to_aws(path: Path) -> str:
    s3 = boto3.resource("s3")
    key = f"{path.parent.name}/{path.name}"

    with open(path, "rb") as data:
        s3.Bucket(AWS_BUCKET).put_object(Key=key, Body=data)
    
    logger.info(f"{path.name} uploaded to bucket: s3://{AWS_BUCKET}/{key}")
    return key


@run_async
async def fetch_contents(aws_key: str) -> Path:
    article_url_df = pd.read_parquet(f"s3://{AWS_BUCKET}/{aws_key}")
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    ingestion_timestamp = pendulum.now()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for article_url in article_url_df["link"].values:
            task = asyncio.create_task(fetch_article_content(session, semaphore, article_url))
            tasks.append(task)
        contents = await asyncio.gather(*tasks)

    data = [
        {
            "article_id": id,
            "content": content,
            "ingested_at": ingestion_timestamp
        } for id, content in zip(article_url_df["article_id"].values, contents)
    ]

    logger.info(f"Contents scrapped at: {ingestion_timestamp.strftime("%d/%m/%Y %H:%M:%S")}")
    return save_to_parquet(data, ingestion_timestamp, CONTENT_PATH)
    

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


