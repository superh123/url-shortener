import datetime

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import Base

class urls(Base):
    __tablename__ = "url_store"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    original_url: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class clicks(Base):
    __tablename__ = "clicks_store"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str] = mapped_column(ForeignKey("url_store.short_code"))
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    ip_address: Mapped[str] = mapped_column(String)
    user_agent: Mapped[str] = mapped_column(String)