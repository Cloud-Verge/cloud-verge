import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from utils.caches import \
    DownloadDemand, downloads_cache, \
    UploadDemand, uploads_cache

from utils.validations import check_admin_auth

router = APIRouter()


@router.post("/upload")
async def post_ask_upload(
    request: Request,
    data: UploadDemand,
):
    if not check_admin_auth(request.headers):
        return JSONResponse({
            "status": "error",
            "message": "Access denied",
        }, status_code=401)

    request_id = str(uuid.uuid4())
    uploads_cache[request_id] = data

    return JSONResponse({
        "status": "ok",
        "url": "/operation/upload/" + request_id,
    })


@router.post("/download")
async def post_ask_download(
    request: Request,
    data: DownloadDemand,
):
    if not check_admin_auth(request.headers):
        return JSONResponse({
            "status": "error",
            "message": "Access denied",
        }, status_code=401)

    request_id = str(uuid.uuid4())
    downloads_cache[request_id] = data

    return JSONResponse({
        "status": "ok",
        "url": "/operation/download/" + request_id,
    })
