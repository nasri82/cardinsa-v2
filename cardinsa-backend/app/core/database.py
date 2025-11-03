# app/core/database.py
from __future__ import annotations

import datetime as dt
import uuid
from typing import Generator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from app.core.settings import settings


# -------------------------------------------------------------------
# Engine
# -------------------------------------------------------------------
def _get(name: str, default):
    # tolerate missing settings while keeping good defaults
    return getattr(settings, name, default)

# DATABASE_URL is required - fail early if not configured
if not hasattr(settings, "DATABASE_URL") or not settings.DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not configured. Please set DATABASE_URL in your .env file. "
        "See .env.example for the correct format."
    )

engine = create_engine(
    settings.DATABASE_URL,
    echo=_get("DB_ECHO", False),
    pool_pre_ping=_get("DB_POOL_PRE_PING", True),
    pool_size=_get("DB_POOL_SIZE", 10),
    max_overflow=_get("DB_MAX_OVERFLOW", 20),
    future=True,
)


# -------------------------------------------------------------------
# Session factory (use get_db dependency in routes)
# -------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,   # keeps objects usable after commit in request scope
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for a scoped SQLAlchemy session.
    Usage:
        def route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------
# Declarative Base with Alembic-friendly naming conventions
# -------------------------------------------------------------------
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# -------------------------------------------------------------------
# Reusable mixins (UUID PK, timestamps, soft delete)
# -------------------------------------------------------------------
def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

class TimestampMixin:
    created_at: Mapped[dt.datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)


# -------------------------------------------------------------------
# Optional helpers
# -------------------------------------------------------------------
def init_engine() -> None:
    """
    Call this on startup if you need to test connectivity early or register
    DB-level options (e.g., Postgres extensions) outside Alembic.
    Keep migrations in Alembic; do NOT call Base.metadata.create_all() here.
    """
    with engine.begin() as _:
        # Example (uncomment if you manage extensions here):
        # _.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        pass


__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "init_engine",
]
