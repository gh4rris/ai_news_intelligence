from database import Base
from .raw_article import RawArticleModel
from .nlp_article import NLPArticleModel


__all__ = [Base, RawArticleModel, NLPArticleModel]