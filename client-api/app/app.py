from fastapi import FastAPI

from .config import AppCofig
from .routes import router


def create_app(config: AppCofig) -> FastAPI:
    app = FastAPI(
        routes=router.routes
    )
    return app
