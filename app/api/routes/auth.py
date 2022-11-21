from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from pydantic import BaseModel

from app.api.auth_utils import verify_password, oauth2_scheme
from app.crud.user import UserCRUD
from app.models.user import UserCreate, User

router = APIRouter()

SECRET_KEY = "temp"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


async def authenticate_user(username: str, password: str, user_crud: UserCRUD) -> Optional[User]:
    user: Optional[User] = await (user_crud.read(username=username))
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
    user: Optional[User] = await user_crud.read(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post(
    "/login",
    summary="Login user and assign token",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login_user(
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

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/signup",
    summary="Create new user",
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def signup_user(
        user_data: UserCreate, user_crud: UserCRUD = Depends(UserCRUD)
) -> User:
    user = user_crud.read(user_data.username)
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
