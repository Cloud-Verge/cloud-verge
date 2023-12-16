import os

from fastapi import FastAPI

from app.config import AppConfig
from app.models.base import Base
from app.routes import router
from app.utils.depends import engine


async def on_startup():
    if not os.path.isdir(AppConfig().local_folder):
        os.makedirs(AppConfig().local_folder)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app() -> FastAPI:
    app = FastAPI(
        routes=router.routes,
        on_startup=[on_startup],
    )
    return app
