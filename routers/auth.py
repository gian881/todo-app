import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import EmailStr

from data.auth import Token, SessionCreate
from data.exceptions import UserNotFoundException, UserAlreadyExistsException
from data.user import Login, User, UserCreate, UserUpdate
from dependencies import DB, get_current_user
from utils import is_email_or_username

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    try:
        if is_email_or_username(username) == Login.EMAIL:
            user = DB.get_user_by_email(email=username)
        else:
            user = DB.get_user_by_username(username=username)
        if not verify_password(password, user.password):
            return None
        return User.from_user_in_db(user)
    except UserNotFoundException:
        return None


def create_access_token() -> str:
    return uuid.uuid4().hex


@router.post('/register', tags=['auth'])
async def register(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()]
):
    user = UserCreate(username=username, password=password, email=email)

    try:

        user.password = get_password_hash(user.password)
        DB.create_user(user)
        return {
            'detail': 'User created successfully'
        }
    except UserAlreadyExistsException as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.post("/token", tags=['auth'])
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token()

    DB.create_session(SessionCreate(
        token=access_token,
        user_id=user.id,
        expires_at=datetime.datetime.now() + datetime.timedelta(days=30)
    ))

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.put('/me', response_model=User)
def update_user(
        current_user: Annotated[User, Depends(get_current_user)],
        username: Annotated[str | None, Form()] = None,
        password: Annotated[str | None, Form()] = None,
        email: Annotated[EmailStr | None, Form()] = None
):
    try:
        DB.update_user(UserUpdate(
            username=username,
            password=password,
            email=email,
            id=current_user.id
        ))
    except UserAlreadyExistsException as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )
