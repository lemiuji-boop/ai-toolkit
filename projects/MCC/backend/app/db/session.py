"""Асинхронная сессия SQLAlchemy (обвязка T-02; миграции Alembic — отдельная задача)."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

_engine = create_async_engine(settings.database_url, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session


async def init_db() -> None:
    """Создание схемы из app/db/models.py на старте (create_all).

    Временная замена миграций: Alembic не настроен (T-02/T-03 — см. OPEN_QUESTIONS).
    create_all идемпотентен и не меняет существующие таблицы.
    """
    from app.db.models import Base

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
