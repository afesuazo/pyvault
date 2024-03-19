from typing import Optional, List

from pydantic import EmailStr, field_validator
from sqlmodel import AutoString, Field, Relationship, SQLModel


# Data only model used by all CRUD operations
class UserBase(SQLModel):
    # Used for password recovery
    email: EmailStr = Field(unique=True, sa_type=AutoString)
    username: str = Field(unique=True)


# Includes full model database representation
class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    hashed_password: str
    public_key: str
    private_key: str
    credentials: List["Credential"] = Relationship(back_populates="owner")


# Adds fields used only during registration
class UserCreate(UserBase):
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str):
        # Constraint length, permit only alphanumeric
        if len(value) < 3 or len(value) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not value.isascii():
            raise ValueError('Username must contain only ASCII characters')
        return value

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, value: str):
        # Constraint length
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value


class UserCreateInternal(UserCreate):
    public_key: str
    private_key: str


# Allows for modifications of all base fields and password
class UserUpdate(UserBase):
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, value: str):
        # Constraint length
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value


class UserRead(UserBase):
    public_key: str


class UserRegistrationRead(UserRead):
    private_key: str
