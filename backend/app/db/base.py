"""Database engine, session factory, and declarative base."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


def build_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine from the given or configured URL."""
    url = database_url or get_settings().database_url
    connect_args: dict = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args, echo=False)


def build_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the given engine."""
    if engine is None:
        engine = build_engine()
    return sessionmaker(bind=engine, expire_on_commit=False)
