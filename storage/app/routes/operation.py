import os
import uuid

import aiofiles
import aiohttp

from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import AppConfig
from models.file import FileEntry

from utils.caches import downloads_cache, uploads_cache
from utils.depends import on_db_session, on_balancer_session
from utils.validations import get_token

router = APIRouter()


@router.put("/upload/{request_id}")
async def put_upload(
    request: Request,
    request_id: str,
    file: UploadFile = File(),
    db_session: AsyncSession = Depends(on_db_session),
    balancer_session: aiohttp.ClientSession = Depends(on_balancer_session),
):
    if request_id not in uploads_cache:
        return JSONResponse({
            "status": "error",
            "message": "Request ID not found",
        }, status_code=404)
    upload = uploads_cache[request_id]

    if request.cookies.get("tmp-storage-auth") != upload.user_auth:
        return JSONResponse({
            "status": "error",
            "message": "Authorization failed",
        }, status_code=401)

    chunk_size = AppConfig.CHUNK_SIZE * 1024
    expected_size = chunk_size * 1024 * 1024  # may vary
    local_path = os.path.join(AppConfig.LOCAL_FOLDER, str(uuid.uuid4()))

    space_used = 0
    async with aiofiles.open(local_path, "wb+") as f:
        while chunk := await file.read(chunk_size):
            space_used += len(chunk)
            if space_used > expected_size:
                break
            await f.write(chunk)

    if space_used > expected_size:
        os.remove(local_path)
        return JSONResponse({
            "status": "error",
            "message": "File size exceeds expected size",
        }, status_code=400)

    file_id = upload.file_id
    async with db_session.begin():
        db_session.add(
            FileEntry(id=file_id, filename=file.filename, local_path=local_path)
        )
        await db_session.commit()

    async with balancer_session.post("/balancer/update_file_info", json={
        "id": file_id,
        "location": AppConfig.LOCATION,
        "filename": file.filename,
        "operation": "ADD",
    }) as resp:
        result = await resp.json()
        if result["status"] != "ok":
            os.remove(local_path)
            return JSONResponse(result, status_code=resp.status)

    uploads_cache.pop(request_id)

    return JSONResponse({
        "status": "ok",
        "file_id": file_id,
    })


@router.get("/download/{request_id}")
async def get_download(
    request: Request,
    request_id: str,
    db_session: AsyncSession = Depends(on_db_session),
):
    if request_id not in downloads_cache:
        return JSONResponse({
            "status": "error",
            "message": "Request ID not found",
        }, status_code=404)
    download = downloads_cache[request_id]

    file_id = download.file_id

    if request.cookies.get("tmp-storage-auth") != download.user_auth:
        return JSONResponse({
            "status": "error",
            "message": "Authorization failed",
        }, status_code=401)

    async with db_session.begin():
        result = await db_session.execute(
            select(FileEntry).where(FileEntry.id == file_id)
        )
        file = result.scalar_one_or_none()

    if file is None:
        return JSONResponse({
            "status": "error",
            "message": "Requested file ID not found",
        }, status_code=404)

    if os.path.isfile(file.local_path):
        downloads_cache.pop(request_id)
        return FileResponse(file.local_path, filename=file.filename)
    else:
        return JSONResponse({
            "status": "error",
            "message": "Unable to find locale file in storage",
        }, status_code=410)
