from fastapi import APIRouter

from .files import router as files_routes

router = APIRouter()

router.include_router(files_routes, prefix='/files')
