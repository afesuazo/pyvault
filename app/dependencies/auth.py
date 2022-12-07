from typing import Optional

from fastapi import Depends, HTTPException
from fastapi import status

from jose import JWTError, jwt
from pydantic import BaseModel

from app.api.auth_utils import oauth2_scheme
from app.crud.user import UserCRUD
from app.models.user import User
from config import SECRET_KEY, ALGORITHM


class TokenData(BaseModel):
    username: str | None = None


async def get_current_user(token: str = Depends(oauth2_scheme), user_crud: UserCRUD = Depends(UserCRUD)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user: Optional[User] = await user_crud.read_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
