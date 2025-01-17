import datetime
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models import User
from service import get_user_by_address
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS
from db import get_async_session

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        s: AsyncSession = Depends(get_async_session)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        address = payload.get("wallet_address")
        if not address:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = await get_user_by_address(s, address)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_admin_user(user: User = Depends(get_current_user)):
    if user.address.lower() != '0x6297d5267f39c99991e70465e7cbf6f6f5f8f6f4':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")
    return user


def create_jwt(wallet_address: str):
    payload = {
        "wallet_address": wallet_address,
        "exp": datetime.datetime.now() + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)