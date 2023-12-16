from starlette.datastructures import Headers

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserData


async def parse_user(db: AsyncSession, headers: Headers) -> UserData | None:
    method, data = headers.get("Authorization", "NO None").split(maxsplit=1)
    if method == "OAuth":
        result = await db.execute(
            select(UserData).where(UserData.oauth_token == data)
        )
        return result.scalar_one_or_none()
    return None
