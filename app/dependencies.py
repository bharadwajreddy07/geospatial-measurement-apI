from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.security import decode_user_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    try:
        user_id = decode_user_id(token)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error), headers={"WWW-Authenticate": "Bearer"}) from error
    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    return user


CurrentUser = Annotated[User, Depends(current_user)]