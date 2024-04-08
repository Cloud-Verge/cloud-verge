from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.config import AppConfig
from utils.depends import on_db_session, on_current_user

from models.user import UserData

import jwt
import datetime
import string


class UserAuthModel(BaseModel):
    email: str
    password: str


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AppConfig.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@router.route('/register')
async def register(user_data: UserAuthModel, db_session: AsyncSession = Depends(on_db_session)):
    email_subseq = ['@gmail.com', '@mail.ru', '@yandex.ru']
    valid_chars = set(string.ascii_letters + string.digits + "_-.@$")

    if all(email_subseq) not in user_data.email:
        return JSONResponse({
            "status": "error",
            "message": "Given email is invalid",
        }, status_code=400)

    if any(ch not in valid_chars for ch in user_data.email):
        return JSONResponse({
            "status": "error",
            "message": "Email contains forbidden symbols",
        }, status_code=400)

    if len(user_data.email) < 5 or len(user_data.password) < 5:
        return JSONResponse({
            "status": "error",
            "message": "Email and password should contain at least 5 symbols",
        }, status_code=400)

    password_hash = get_password_hash(user_data.password)

    async with db_session.begin():
        db_session.add(UserData(
            username=user_data.username,
            password_hash=password_hash
        ))
        await db_session.commit()

    return JSONResponse({
        "status": "ok",
        "message": "User registered successfully",
    }, status_code=200)


@router.route('/login')
async def login(user_data: UserAuthModel, db_session: AsyncSession = Depends(on_db_session)):
    async with db_session.begin():
        user = await db_session.execute(
            select(UserData).where(UserData.email == user_data.email)
        )
        user = user.scalar_one_or_none()
        if user is None:
            return JSONResponse({
                "status": "error",
                "message": "User does not exist",
            }, status_code=401)

    if not verify_password(user_data.password, user.password_hash):
        return JSONResponse({
            "status": "error",
            "message": "Invalid password",
        }, status_code=401)

    jwt_token = create_access_token(data={"sub": user.id})
    return JSONResponse({
        "status": "ok",
        "message": "Successful auth",
        "token": jwt_token,
    }, status_code=200)


@router.route('/update_password')
async def update_password(
    new_password: str,
    db_session: AsyncSession = Depends(on_db_session),
    user_id: int = Depends(on_current_user),
):
    async with db_session.begin():
        user = await db_session.execute(
            select(UserData).where(UserData.id == user_id)
        )
        user = user.scalar_one_or_none()
        if user is None:
            return JSONResponse({
                "status": "error",
                "message": "Invalid user",
            }, status_code=403)

    if new_password:
        user.password_hash = get_password_hash(new_password)
    return JSONResponse({
        "status": "ok",
        "message": "Password updated successfully",
    }, status_code=200)
