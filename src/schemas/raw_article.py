from pydantic import BaseModel
from datetime import datetime


class RawArticle(BaseModel):
    article_id: str
    title: str | None
    url: str
    source_name: str
    author: str | None
    summary: str | None
    published_at: datetime | None
    ingested_at: datetime
    content: str