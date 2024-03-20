from fastapi import FastAPI

from models.base import Base
from routes import router
from utils.depends import engine


async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(
    routes=router.routes,
    on_startup=[on_startup],
)
