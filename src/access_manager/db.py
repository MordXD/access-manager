from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.access_manager.core.config import settings

DATABASE_URL = str(settings.postgres_dsn)  # ожидается async-DSN: postgres+asyncpg://...

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
