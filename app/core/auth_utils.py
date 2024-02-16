from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt

from config import SECRET_KEY, ALGORITHM

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="JWT")


def create_access_token(user: str, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    # Default expiration time is 15 minutes
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": user}
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)
