import uuid

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

from typing import Literal
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.file import FileEntry
from utils.depends import on_db_session, on_storage_session
from utils.validations import parse_user

router = APIRouter()


class AskUploadModel(BaseModel):
    size: int
    access: Literal["PRIVATE", "PUBLIC"] = "PUBLIC"


@router.post("/ask_upload")
async def post_ask_upload(
    request: Request,
    data: AskUploadModel,
    db_session: AsyncSession = Depends(on_db_session),
    storage_session: aiohttp.ClientSession = Depends(on_storage_session),
):
    async with db_session.begin():
        user = await parse_user(db_session, request.headers)
        if user is None:
            return JSONResponse({
                "status": "error",
                "message": "Authorization failed",
            }, status_code=401)

    file_id = str(uuid.uuid4())
    async with storage_session.post("/demands/upload", json={
        "size": data.size,
        "user_token": user.oauth_token,
        "file_id": file_id,
    }) as resp:
        base_url = str(resp.url).removesuffix("/demands/upload")
        base_url = base_url.replace("host.docker.internal", "localhost")
        result = await resp.json()
        if result["status"] != "ok":
            return JSONResponse(result, status_code=resp.status)

    file_access = 0 if data.access == "PUBLIC" else -1
    async with db_session.begin():
        db_session.add(FileEntry(
            id=file_id,
            owner=user.id,
            access=file_access,
            locations=[]
        ))
        await db_session.commit()

    return JSONResponse({
        "status": "ok",
        "url": base_url + result["url"],
    })


@router.get("/download/{file_id}")
async def get_download(
    request: Request,
    file_id: str,
    db_session: AsyncSession = Depends(on_db_session),
    storage_session: aiohttp.ClientSession = Depends(on_storage_session),
):
    async with db_session.begin():
        file = await db_session.execute(
            select(FileEntry).where(FileEntry.id == file_id)
        )
        file = file.scalar_one_or_none()
        if file is None:
            return JSONResponse({
                "status": "error",
                "message": "File not found",
            }, status_code=404)

        if file.access != 0:
            user = await parse_user(db_session, request.headers)
            if user is None or user.id != file.owner:
                return JSONResponse({
                    "status": "error",
                    "message": "Access denied",
                }, status_code=401)
            user_token = user.oauth_token
        else:
            user_token = None

    try:
        async with storage_session.post("/demands/download", json={
            "file_id": file_id,
            "user_token": user_token,
        }) as resp:
            base_url = str(resp.url).removesuffix("/demands/download")
            base_url = base_url.replace("host.docker.internal", "localhost")
            result = await resp.json()
            if result["status"] != "ok":
                return JSONResponse(result, status_code=resp.status)
    except ClientConnectionError:
        return JSONResponse({
                "status": "error",
                "message": "Unable to contact storage",
            }, status_code=500)

    return RedirectResponse(base_url + result["url"])


@router.get("/list")
async def get_files_list(
    request: Request,
    db_session: AsyncSession = Depends(on_db_session),
):
    async with db_session.begin():
        user = await parse_user(db_session, request.headers)
        if user is None:
            return JSONResponse({
                "status": "error",
                "message": "Authorization failed",
            }, status_code=401)

        result = await db_session.execute(
            select(FileEntry).where(FileEntry.owner == user.id)
        )

    files = []
    for entry in result.scalars():
        if entry.locations:
            files.append({
                "file_id": entry.id,
                "filename": entry.filename,
                "created_at": entry.created_at.isoformat(),
            })

    return JSONResponse({
        "status": "ok",
        "result": files,
    })
