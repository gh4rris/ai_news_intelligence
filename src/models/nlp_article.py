from . import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime


class NLPArticleModel(Base):
    __tablename__ = "nlp_articles"

    article_id: Mapped[str] = mapped_column(String, ForeignKey("raw_articles.article_id"), primary_key=True)
    sentiment: Mapped[str] = mapped_column(String)
    sentiment_score: Mapped[float] = mapped_column(Float)
    topics: Mapped[list[str]] = mapped_column(JSONB)
    entities: Mapped[list[dict[str, str]]] = mapped_column(JSONB)
    processed_at: Mapped[datetime] = mapped_column(DateTime)