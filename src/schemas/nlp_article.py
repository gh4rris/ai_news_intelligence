from pydantic import BaseModel
from datetime import datetime


class NLPArticle(BaseModel):
    article_id: str
    sentiment: str
    sentiment_score: float
    topics: list[str]
    entities: list[dict[str, str]]
    processed_at: datetime