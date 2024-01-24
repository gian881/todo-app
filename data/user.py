from enum import Enum

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    id: int
    username: str | None = None
    password: str | None = None
    email: EmailStr | None = None


class User(BaseModel):
    id: int
    username: str
    email: EmailStr

    @classmethod
    def from_user_in_db(cls, user):
        return cls(
            username=user.username,
            id=user.id,
            email=user.email,
        )


class UserInDb(User):
    password: str


class Login(Enum):
    USERNAME = 0
    EMAIL = 1
