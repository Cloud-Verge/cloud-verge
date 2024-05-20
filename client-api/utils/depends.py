from aiohttp import ClientSession

import jwt

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .config import AppConfig

engine: AsyncEngine = create_async_engine(AppConfig.SQL_ENGINE_URI)
security = HTTPBearer(auto_error=False)


async def on_db_session():
    """Usage:
    @app.get('/method/')
    async def method(session: AsyncSession = Depends(on_db_session))
        ...
    """

    session_fabric = async_sessionmaker(engine, expire_on_commit=False)
    async with session_fabric() as session:
        yield session


async def on_storage_session():
    """Usage:
    @app.get('/method/')
    async def method(session: aiohttp.ClientSession = Depends(on_storage_session))
        ...
    """

    async with ClientSession(base_url=AppConfig.STORAGE_URL, headers={
        "Authorization": "OAuth " + AppConfig.STORAGE_TOKEN,
        "User-Agent": "CloudVerge Node",
    }) as session:
        yield session


async def on_current_user(http_auth: HTTPAuthorizationCredentials = Security(security)):
    if http_auth is None:
        return None

    try:
        payload = jwt.decode(http_auth.credentials, AppConfig.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="User not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id


async def on_current_user_force(http_auth: HTTPAuthorizationCredentials = Security(security)):
    user_id = await on_current_user(http_auth)
    if user_id is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return user_id
