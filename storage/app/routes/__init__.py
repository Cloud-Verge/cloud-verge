from fastapi import APIRouter

from .demands import router as demands_routes
from .operation import router as operation_routes

router = APIRouter()

router.include_router(demands_routes, prefix='/demands')
router.include_router(operation_routes, prefix='/operation')
