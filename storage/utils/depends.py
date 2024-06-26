from aiohttp import ClientSession

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import AppConfig

engine: AsyncEngine = create_async_engine(AppConfig.SQL_ENGINE_URI)


async def on_db_session():
    """Usage:
    @app.get('/method/')
    async def method(session: AsyncSession = Depends(on_db_session))
        ...
    """

    session_fabric = async_sessionmaker(engine, expire_on_commit=False)
    async with session_fabric() as session:
        yield session


async def on_balancer_session():
    """Usage:
    @app.get('/method/')
    async def method(session: aiohttp.ClientSession = Depends(on_balancer_session))
        ...
    """

    async with ClientSession(base_url=AppConfig.BALANCER_URL, headers={
        "Authorization": "OAuth " + AppConfig.BALANCER_TOKEN,
        "User-Agent": "CloudVerge Node",
    }) as session:
        yield session
