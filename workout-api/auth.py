# Datetime is for Expiration of JWT
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
# Basemodel For Validation of the user
from pydantic import BaseModel
from sqlalchemy.orm import Session
# Status for Returning correct status code back to the user
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
# Form To Pass 2 Password auth
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# For Debugging
import logging


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


# Using Them in bottom section
SECRET_KEY = 'ASDHHMKLdfeyuol2312478msasdasdgaSADDEWGfh5478dsfwasd'
# Using Standard algorithm HS256
ALGORITHM = 'HS256'


# Password Hashing and Unhashing
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



# Data Validation
class CreateUserRequest(BaseModel):
    username: str
    fullname : str
    mail: str
    phone: str #Its String Because of prefixes user might input
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Dependency For Database

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]



# Creating User Model
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest): # Passing CreateUserRequest for field Validation

    create_user_model = User(
        username = create_user_request.username,
        fullname = create_user_request.fullname,
        mail = create_user_request.mail,
        phone = create_user_request.phone,
        hashed_password = bcrypt_context.hash(
            create_user_request.password
            ) # Hashing Password To hs256 algorithm
    )

    #Commiting Db Additions
    db.add(create_user_model)
    db.commit() 


# authentificating users using custom made function that queries user
@router.post("/token", response_model=Token)
async def login_for_access_token(
form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=60)) # Time For Token To be alive
    return {'access_token': token, 'token_type': 'bearer'}  # Returning a dictionary

# custom made function that queries user
def authenticate_user(username: str, password: str, db):
    #Quering User By Unique Username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    #Checking Decrypted password with .verify
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


#JWT Encoding
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


#JWT Decoding
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # If Decoded Fails, We raise an exception down below
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Decoding username and user_id
        username: str = decoded.get('sub')
        user_id: int = decoded.get('id')
        # Checking For username to not be none / user_id to not be none
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')