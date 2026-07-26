import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

db_url = os.environ.get("DATABASE_URL", "sqlite:///./urls.db").replace("postgres://", "postgresql://", 1)
engine = create_engine(db_url)

# engine = create_engine("sqlite:///test2.db", echo=True)

class Base(DeclarativeBase):
    pass