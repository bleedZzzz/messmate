"""FastAPI dependency injection providers."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.api.middleware import check_rate_limit
from app.config import get_settings
from app.db.base import build_engine, build_session_factory
from app.llm.base import GroqProvider, LLMProvider, NoneProvider

# Cached factory instance
_session_factory = None


def get_session_factory():
    """Return singleton session factory."""
    global _session_factory
    if _session_factory is None:
        engine = build_engine()
        _session_factory = build_session_factory(engine)
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """Dependency yielding a database Session."""
    factory = get_session_factory()
    with factory() as session:
        yield session


def get_llm() -> LLMProvider:
    """Dependency providing configured LLMProvider."""
    settings = get_settings()
    provider_name = settings.llm_provider.lower().strip()

    if provider_name == "groq" and settings.groq_api_key:
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.llm_model or None,
        )

    # Defaults to NoneProvider (no LLM, purely deterministic fallback)
    return NoneProvider()


__all__ = [
    "check_rate_limit",
    "get_db",
    "get_llm",
]
