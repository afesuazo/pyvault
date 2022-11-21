from typing import Optional

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth_utils import verify_password
from app.crud.user import UserCRUD
from app.models.user import UserCreate, User

router = APIRouter()


async def authenticate_user(username: str, password: str, user_crud: UserCRUD = Depends(UserCRUD)):
    user: Optional[User] = await user_crud.read(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post(
    "/login",
    summary="Login user and assign token",
    response_model=User,
    status_code=status.HTTP_200_OK
)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends()
) -> User:

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return user


@router.post(
    "/signup",
    summary="Create new user",
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def signup_user(
        user_data: UserCreate, user_crud: UserCRUD = Depends(UserCRUD)
) -> User:
    user = await user_crud.create(user_data=user_data)
    return user
