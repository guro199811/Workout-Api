# Datetime is for Expiration of JWT
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

# Form To Pass 2 Password auth
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

import logging

from database import SessionLocal
from models import User
from form_models import CreateUserRequest, Token


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# For User Authentification

auth = APIRouter(prefix="/auth", tags=["auth"])


# Using Them in bottom section
SECRET_KEY = "ASDHHMKLdfeyuol2312478msasdasdgaSADDEWGfh5478dsfwasd"
# Using Standard algorithm HS256
ALGORITHM = "HS256"


# Password Hashing and Unhashing
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


# Dependency For Database


# Creating User Model
@auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    description="Endpoint for user creation/registration",
)
async def create_user(
    db: db_dependency, create_user_request: CreateUserRequest
):  # Passing CreateUserRequest for field Validation

    create_user_model = User(
        username=create_user_request.username,
        fullname=create_user_request.fullname,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        weight=create_user_request.weight,
        height=create_user_request.height,
        active=create_user_request.active,
    )

    # Commiting Db Additions
    try:
        db.add(create_user_model)
        db.commit()
        return {"User": "Created Succesfully"}
    except Exception as e:
        logging.error(f"in auth.create_user, exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username Already Exists / Taken",
        )


@auth.post(
    "/token",
    response_model=Token,
    description="Returns token, which is used to authenticate user",
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    # authenticate_user is a function that verifies the user's data
    # it also decrypts bcrypted/hashed password
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
    token = create_access_token(
        user.username, user.user_id, timedelta(minutes=60)
    )  # Time For Token To be alive
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(username: str, password: str, db):
    # Quering User By Unique Username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find specified username.",
        )
    # Checking Decrypted password with .verify
    if not bcrypt_context.verify(password, user.hashed_password):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is not Bcrypted.",
        )
    return user


# JWT Encoding
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    try:
        encode = {"sub": username, "id": user_id}
        expires = datetime.utcnow() + expires_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError:
        logging.error(f"in auth.create_access_token exception: {JWTError}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cant Encode The request."
        )


# JWT Decoding
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # If Decode Fails, We raise an exception
        decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = decode.get("sub")
        user_id: int = decode.get("id")
        # Checking For username to not be none / user_id to not be none
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id}
    except JWTError:
        logging.error(f"in auth.create_access_token exception: {JWTError}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
