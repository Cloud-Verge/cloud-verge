import os

from fastapi import FastAPI

from app.config import AppConfig
from app.models.base import Base
from app.routes import router
from app.utils.depends import engine


async def on_startup():
    if not os.path.isdir(AppConfig.LOCAL_FOLDER):
        os.makedirs(AppConfig.LOCAL_FOLDER)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(
    routes=router.routes,
    on_startup=[on_startup],
)
