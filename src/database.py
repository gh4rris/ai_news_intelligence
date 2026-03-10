from config import DB_URL

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


engine = sa.create_engine(DB_URL)
Session = sessionmaker(bind=engine)