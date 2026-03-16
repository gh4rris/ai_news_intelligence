from config import SENTIMENT_MODEL
from models import RawArticleModel, ArticleNLPModel
from database import Session

import sqlalchemy as sa
from transformers import pipeline


sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL)


def get_unprocessed_articles():
    statement = sa.select(
        RawArticleModel.article_id,
        RawArticleModel.title
        ).outerjoin(ArticleNLPModel).where(ArticleNLPModel.article_id == None)
    
    with Session() as session:
        rows = session.execute(statement).fetchall()

    return rows

x = get_unprocessed_articles()
print(x)
print(type(x))


def get_sentiment(text: str) -> tuple[str, float]:
    result = sentiment_pipeline(text)[0]
    return result["label"], result["score"]