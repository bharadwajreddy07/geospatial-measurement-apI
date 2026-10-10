from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine_options = {"pool_pre_ping": True}
if not settings.database_url.startswith("sqlite"):
    engine_options.update(pool_size=10, max_overflow=20)
engine = create_async_engine(settings.database_url, **engine_options)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


async def create_tables() -> None:
    from app import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)