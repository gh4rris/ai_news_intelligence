from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from datetime import datetime

Base = declarative_base()

class RawData(Base):
    __tablename__ = "raw_data"

    article_id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    url: Mapped[str]
    source_name: Mapped[str]
    author: Mapped[str]
    summary: Mapped[str]
    published_at: Mapped[datetime]
    content: Mapped[str]
