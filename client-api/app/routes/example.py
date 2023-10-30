from fastapi import APIRouter, Depends, HTTPException, Response

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserData
from utils.depends import on_db_session

router = APIRouter()


@router.get('/get_user/{token}')
async def get_user(
    token: str,
    session: AsyncSession = Depends(on_db_session)
):
    """
    Don't use it in prod, it's just an example
    """
    async with session.begin():
        result = await session.execute(
            select(UserData).where(UserData.oauth_token == token)
        )
        user = result.scalar_one_or_none()

    if user is None:
        HTTPException(404, "User not found")
    return Response({
        'user_id': user.id,
        'oauth_token': user.oauth_token
    })
