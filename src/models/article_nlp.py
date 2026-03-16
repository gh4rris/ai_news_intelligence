from . import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Float, Text, DateTime
from datetime import datetime


class ArticleNLPModel(Base):
    __tablename__ = "article_nlp"

    article_id: Mapped[str] = mapped_column(String, ForeignKey("raw_articles.article_id"), primary_key=True)
    sentiment: Mapped[str] = mapped_column(String)
    sentiment_score: Mapped[float] = mapped_column(Float)
    topic: Mapped[str] = mapped_column(String)
    entities: Mapped[str] = mapped_column(Text)
    processed_at: Mapped[datetime] = mapped_column(DateTime)