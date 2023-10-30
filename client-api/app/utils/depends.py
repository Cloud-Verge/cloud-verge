from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy.engine.url import URL

engine: AsyncEngine = None


def init_database(url: str | URL, **kw):
    global engine
    engine = create_async_engine(url, **kw)


async def on_db_session():
    """Usage:
    @app.get('/method/')
    async def method(session: AsyncSession = Depends(on_db_session))
        ...
    """

    if engine is None:
        raise RuntimeError(
            "SQLAlchemy engine is not initialized. Call init_database(url) to initialize"
        )

    session_fabric = async_sessionmaker(engine, expire_on_commit=False)
    async with session_fabric() as session:
        yield session
