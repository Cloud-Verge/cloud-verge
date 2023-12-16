from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from typing import Literal, Optional
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import FileEntry
from app.utils.depends import on_db_session
from app.utils.validations import check_admin_auth

router = APIRouter()


class FileInfoUpdate(BaseModel):
    id: str
    location: str
    filename: Optional[str]
    operation: Literal["ADD", "DELETE"]


@router.post("/update_file_info")
async def update_file_info(
    request: Request,
    data: FileInfoUpdate,
    db_session: AsyncSession = Depends(on_db_session),
):
    if not check_admin_auth(request.headers):
        return JSONResponse({
            "status": "error",
            "message": "Access denied",
        }, status_code=401)

    async with db_session.begin():
        result = await db_session.execute(
            select(FileEntry).where(FileEntry.id == data.id)
        )
        file = result.scalar_one_or_none()
        if file is None:
            return JSONResponse({
                "status": "error",
                "message": "Requested file ID not found",
            }, status_code=404)

        if data.operation == "ADD" and data.location not in file.locations:
            if data.filename:
                file.filename = data.filename
            file.locations.append(data.location)
        elif data.operation == "DELETE" and data.location in file.locations:
            file.locations.remove(data.location)

    return JSONResponse({"status": "ok"})
