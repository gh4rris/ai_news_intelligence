from ingestion import generate_article_id, parse_date, filter_feed, save_to_parquet, upload_to_s3, fetch_article_content

import pytest
from unittest.mock import AsyncMock
import time
import aiohttp
import asyncio
from pytest_mock import MockFixture
from feedparser import FeedParserDict
from pendulum import DateTime, Timezone, datetime
from pathlib import Path


def test_generate_article_id():
    assert generate_article_id("https://example.com/test-article") == "6b4c16dd598c2e53c58430c6adcfe2b4"


@pytest.mark.parametrize("time_struct, expected", [
    (time.strptime("18/06/2026 01:05:06", "%d/%m/%Y %H:%M:%S"), DateTime(year=2026, month=6, day=18, hour=1, minute=5, second=6, tzinfo=Timezone("UTC"))),
    (time.strptime("18/06/2026", "%d/%m/%Y"), DateTime(year=2026, month=6, day=18, tzinfo=Timezone("UTC"))),
    (time.strptime("18/06/2026 01:05:06 Thursday", "%d/%m/%Y %H:%M:%S %A"), DateTime(year=2026, month=6, day=18, hour=1, minute=5, second=6, tzinfo=Timezone("UTC"))),
    (None, None)
])
def test_parse_date(time_struct, expected):
    fpd = FeedParserDict()
    fpd["published_parsed"] = time_struct
    assert parse_date(fpd) == expected


def test_filter_feed():
    data = [
        {"published_parsed": datetime(year=2026, month=1, day=1)},
        {"published_parsed": datetime(year=2026, month=1, day=2)},
        {"published_parsed": datetime(year=2026, month=1, day=4)},
        {"published_parsed": datetime(year=2026, month=1, day=1, hour=1)},
        {"published_parsed": datetime(year=2026, month=1, day=1, hour=0, minute=0, second=1)},
        {"published_parsed": None}
    ]
    ingested = datetime(year=2026, month=1, day=4)

    expected = [
        {"published_parsed": datetime(year=2026, month=1, day=2)},
        {"published_parsed": datetime(year=2026, month=1, day=4)},
        {"published_parsed": datetime(year=2026, month=1, day=1, hour=1)},
        {"published_parsed": datetime(year=2026, month=1, day=1, hour=0, minute=0, second=1)}
    ]
    assert filter_feed(data, ingested) == expected


def test_save_to_parquet(mocker: MockFixture):
    mock_mkdir = mocker.patch("ingestion.Path.mkdir")
    mock_parquet = mocker.patch("ingestion.pd.DataFrame.to_parquet")
    mock_mkdir.return_value = None
    mock_parquet.return_value = None

    data = [{"test": "data"}]
    ingested = DateTime(year=2026, month=6, day=18)
    path = Path("/test/content/")
    
    assert save_to_parquet(data, ingested, path) == Path("/test/content/2026-06-18_content.parquet")


def test_upload_to_s3(mocker: MockFixture):
    mock_load = mocker.patch("ingestion.S3Hook.load_file")
    mock_load.return_value = None
    
    path = Path("/home/test/feed")
    assert upload_to_s3(path) == "test/feed"


@pytest.mark.parametrize("status, text, expected", [
    (200, "<html><body>Test article</body></html>", "Test article"),
    (201, "<html><body>Test article</body></html>", None),
    (200, "Test article", None),
    (500, None, None)
])
@pytest.mark.asyncio
async def test_fetch_article_content(status, text, expected, mocker: MockFixture):
    mock_get = mocker.patch("ingestion.ClientSession.get")
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.text.return_value = text
    mock_get.return_value.__aenter__.return_value = mock_resp

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore()
        result = await fetch_article_content(session, semaphore, "http://test.com")

    assert result == expected
    
