"""Database engine, connection pooling, and session management."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from retailiq.config import settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_db_url() -> str:
    """Resolve database URL, prioritizing DATABASE_URL env var and defaulting to local SQLite."""
    url = os.environ.get("DATABASE_URL", settings.database_url)
    # If postgresql:// on Render/Heroku uses legacy postgres://, fix it
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def reset_engine() -> None:
    """Reset cached global engine and session factory (useful for tests and dynamic database URLs)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def get_engine() -> Engine:
    """Create or return the global SQLAlchemy engine."""
    global _engine
    if _engine is None:
        url = get_db_url()
        if url.startswith("sqlite"):
            # Ensure SQLite parent directory exists
            if "///" in url:
                path_part = url.split("///")[1]
                Path(path_part).parent.mkdir(parents=True, exist_ok=True)
            _engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            _engine = create_engine(
                url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=300,
                pool_pre_ping=True,
            )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Create or return the sessionmaker factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for acquiring and safely releasing a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize all tables defined in models."""
    from retailiq.database.models import Base

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
