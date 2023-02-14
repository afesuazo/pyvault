from datetime import timedelta
from typing import Optional, List

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel
from fastapi.requests import Request

from app.api.auth_utils import verify_password, create_access_token
from app.api.cypt_utils import generate_master_key
from app.crud.user import UserCRUD
from app.dependencies.auth import get_current_user
from app.models.user import UserCreate, User
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SALT_1

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration_time: int


async def authenticate_user(username: str, password: str, user_crud: UserCRUD) -> Optional[User]:
    user: Optional[User] = await (user_crud.read_by_username(username=username))
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.get("/all-users")
async def temp_users(user_crud: UserCRUD = Depends(UserCRUD)) -> list[User]:
    users = await user_crud.read_many(0, 100)
    return users


@router.post(
    "/login",
    summary="Login user and assign token",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login_user(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_crud: UserCRUD = Depends(UserCRUD)
) -> Token:
    user: Optional[User] = await authenticate_user(form_data.username, form_data.password, user_crud)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    request.session['crypt_key'] = generate_master_key(form_data.password + SALT_1.decode()).hex()
    return Token(access_token=access_token, token_type="bearer", expiration_time=access_token_expires.seconds)


@router.post(
    "/signup",
    summary="Create new user",
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def signup_user(
        user_data: UserCreate, user_crud: UserCRUD = Depends(UserCRUD)
) -> User:
    user = await user_crud.read_by_username(user_data.username)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exist"
        )
    user = await user_crud.create(user_data=user_data)
    return user


@router.get(
    "/me",
    summary='Get details of currently logged in user',
    response_model=User
)
async def get_me(
        user: User = Depends(get_current_user)
) -> User:
    return user
