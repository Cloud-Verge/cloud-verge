from fastapi import APIRouter

from .auth import router as auth_router
from .balancer import router as balancer_routes
from .files import router as files_routes

router = APIRouter()

router.include_router(auth_router, prefix='/auth')
router.include_router(balancer_routes, prefix='/balancer')
router.include_router(files_routes, prefix='/files')
