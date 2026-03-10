from . import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, String, DateTime
from datetime import datetime


class RawDataModel(Base):
    __tablename__ = "raw_data"

    article_id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String, unique=True)
    source_name: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    ingested_at: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[str] = mapped_column(Text)