import uuid
from typing import Optional

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.file import FileEntry
from utils.depends import on_db_session, on_storage_session, on_current_user, on_current_user_force

router = APIRouter()


@router.get("/upload_link")
async def get_upload_link(
    access: Literal["PRIVATE", "PUBLIC"] = "PRIVATE",
    db_session: AsyncSession = Depends(on_db_session),
    storage_session: aiohttp.ClientSession = Depends(on_storage_session),
    user_id: int = Depends(on_current_user_force),
):
    file_id = str(uuid.uuid4())
    user_auth = str(uuid.uuid4())
    async with storage_session.post("/demands/upload", json={
        "user_auth": user_auth,
        "file_id": file_id,
    }) as resp:
        base_url = str(resp.url).removesuffix("/demands/upload")
        base_url = base_url.replace("host.docker.internal", "localhost")
        result = await resp.json()
        if result["status"] != "ok":
            return JSONResponse(result, status_code=resp.status)

    file_access = 0 if access == "PUBLIC" else -1
    async with db_session.begin():
        db_session.add(FileEntry(
            id=file_id,
            owner=user_id,
            access=file_access,
            locations=[]
        ))
        await db_session.commit()

    domain = base_url.removeprefix("http://").removeprefix("https://").split(":", maxsplit=1)[0]

    resp = JSONResponse({
        "status": "ok",
        "url": base_url + result["url"]
    })
    resp.set_cookie(
        "tmp-storage-auth", user_auth,
        domain=domain if domain != "localhost" else None,
        max_age=360, httponly=True,
    )
    return resp


@router.get("/download_link/{file_id}")
async def get_download_link(
    file_id: str,
    db_session: AsyncSession = Depends(on_db_session),
    storage_session: aiohttp.ClientSession = Depends(on_storage_session),
    user_id: Optional[int] = Depends(on_current_user),
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

        if file.access != 0 and user_id != file.owner:
            return JSONResponse({
                "status": "error",
                "message": "Access denied",
            }, status_code=401)

    user_auth = str(uuid.uuid4())

    try:
        async with storage_session.post("/demands/download", json={
            "file_id": file_id,
            "user_auth": user_auth,
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

    domain = base_url.removeprefix("http://").removeprefix("https://").split(":", maxsplit=1)[0]

    resp = JSONResponse({
        "status": "ok",
        "url": base_url + result["url"]
    })
    resp.set_cookie(
        "tmp-storage-auth", user_auth,
        domain=domain if domain != "localhost" else None,
        max_age=360, httponly=True,
    )
    return resp


@router.get("/download/{file_id}")
async def get_download(
    request: Request,
    file_id: str,
    db_session: AsyncSession = Depends(on_db_session),
    storage_session: aiohttp.ClientSession = Depends(on_storage_session),
    user_id: Optional[int] = Depends(on_current_user),
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

        if file.access != 0 and user_id != file.owner:
            return JSONResponse({
                "status": "error",
                "message": "Access denied",
            }, status_code=401)

    user_auth = str(uuid.uuid4())

    try:
        async with storage_session.post("/demands/download", json={
            "file_id": file_id,
            "user_auth": user_auth,
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

    domain = base_url.removeprefix("http://").removeprefix("https://").split(":", maxsplit=1)[0]

    resp = RedirectResponse(base_url + result["url"])
    resp.set_cookie(
        "tmp-storage-auth", user_auth,
        domain=domain if domain != "localhost" else None,
        max_age=360, httponly=True,
    )
    return resp


@router.get("/list")
async def get_files_list(
    db_session: AsyncSession = Depends(on_db_session),
    user_id: int = Depends(on_current_user_force),
):
    async with db_session.begin():
        result = await db_session.execute(
            select(FileEntry).where(FileEntry.owner == user_id)
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
