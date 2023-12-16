import aiohttp
from aiohttp.client_exceptions import ClientConnectionError

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from typing import Literal
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.depends import on_db_session, on_storage_session
from app.utils.validations import parse_user

router = APIRouter()


class AskUploadModel(BaseModel):
    size: int
    access: Literal["PUBLIC"] = "PUBLIC"


class AskDownloadModel(BaseModel):
    file_id: str


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

    async with storage_session.post("/demands/upload", json={
        "size": data.size,
        "access": data.access,
        "user_token": user.oauth_token,
    }) as resp:
        base_url = str(resp.url).removesuffix("/demands/upload")
        result = await resp.json()
        if result["status"] != "ok":
            return JSONResponse(result, status_code=resp.status)

    return JSONResponse({
        "status": "ok",
        "url": base_url + result["url"],
    })


@router.post("/ask_download")
async def post_ask_download(
    request: Request,
    data: AskDownloadModel,
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

    try:
        async with storage_session.post("/demands/download", json={
            "file_id": data.file_id,
        }) as resp:
            base_url = str(resp.url).removesuffix("/demands/download")
            result = await resp.json()
            if result["status"] != "ok":
                return JSONResponse(result, status_code=resp.status)
    except ClientConnectionError:
        return JSONResponse({
                "status": "error",
                "message": "Unable to contact storage",
            }, status_code=500)

    return JSONResponse({
        "status": "ok",
        "url": base_url + result["url"],
    })
