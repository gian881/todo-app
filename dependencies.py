from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from data.db import Database

DB = Database()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    return DB


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        return get_db().get_user_by_token(token)
    except ValueError:
        raise credentials_exception
