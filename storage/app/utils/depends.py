from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import AppConfig

engine: AsyncEngine = create_async_engine(AppConfig().sql_engine_url)


async def on_db_session():
    """Usage:
    @app.get('/method/')
    async def method(session: AsyncSession = Depends(on_db_session))
        ...
    """

    session_fabric = async_sessionmaker(engine, expire_on_commit=False)
    async with session_fabric() as session:
        yield session
