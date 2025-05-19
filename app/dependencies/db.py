from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
