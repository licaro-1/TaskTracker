import sys
from typing import AsyncGenerator
from sqlalchemy.pool import NullPool

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from core.settings import settings


def is_pytest_environment():
    return "pytest" in sys.modules.keys()


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        pool_size: int = 50,
        max_overflow: int = 10,
    ):
        if is_pytest_environment():
            self.engine: AsyncEngine = create_async_engine(url=url, poolclass=NullPool)
        else:
            self.engine: AsyncEngine = create_async_engine(
                url=url,
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )

        self.session_factory: async_sessionmaker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


def get_db_helper() -> DatabaseHelper:
    """return pytest database if code running from pytest module"""
    if is_pytest_environment():
        db_help = DatabaseHelper(
            url=str(settings.pytest_db.url),
        )
    else:
        db_help = DatabaseHelper(
            url=str(settings.db.url),
            echo=settings.db.echo,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )
    return db_help


db_helper = get_db_helper()
