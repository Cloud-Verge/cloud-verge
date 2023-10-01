from fastapi import APIRouter

from .example import router as common_router

router = APIRouter()

router.include_router(common_router, prefix='/api')
