from datetime import timedelta
from typing import Optional, Annotated

from aioredis import Redis
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth_utils import create_access_token
from app.core.cypt_utils import generate_key_pair
from app.crud.user import UserCRUD
from app.dependencies.auth import get_current_user
from app.dependencies.redis import get_redis
from app.models.token import Token
from app.models.user import UserCreate, User, UserRead, UserRegistrationRead, UserCreateInternal
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


# TODO: Move to developer only endpoint and require admin user credentials
@router.get("/all-users", response_model=list[User])
async def temp_users(user_crud: UserCRUD = Depends(UserCRUD)) -> list[User]:
    users = await user_crud.read_many(0, 100)
    return users


@router.post(
    "/register",
    summary="Create new user",
    response_model=UserRegistrationRead,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user_data: UserCreate,
        user_crud: UserCRUD = Depends(UserCRUD)
) -> UserRegistrationRead:
    # Check if user with username or email already exist
    user = await user_crud.read_by_username(user_data.username)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exist"
        )
    user = await user_crud.read_by_email(user_data.email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist"
        )

    # Generate public/private key pair (str)
    public_key, private_key = generate_key_pair()

    # Save user to database
    user_internal_data: UserCreateInternal = UserCreateInternal(**user_data.dict(), public_key=public_key, private_key=private_key)
    user = await user_crud.create(user_data=user_internal_data)
    user_registration_read = UserRegistrationRead(**user.dict(exclude_unset=True))
    return user_registration_read


@router.post(
    "/login",
    summary="Login user and assign token",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_crud: UserCRUD = Depends(UserCRUD),
        redis: Redis = Depends(get_redis)
):
    user: Optional[User] = await user_crud.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username & password combination"
        )

    # Create access token with set expiration time
    access_token_expire_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user=user.username, expires_delta=access_token_expire_time)

    await redis.execute_command('set', f"{str(user.id)}_public", user.public_key, 'ex', ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    await redis.execute_command('set', f"{str(user.id)}_private", user.private_key, 'ex', ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    token = Token(access_token=access_token, token_type="bearer", expiration_time=access_token_expire_time.seconds)
    return token


@router.get(
    "/me",
    summary='Get details for currently logged in user',
    response_model=UserRead
)
async def get_me(
        user: User = Depends(get_current_user)
) -> UserRead:
    return UserRead(**user.dict())
