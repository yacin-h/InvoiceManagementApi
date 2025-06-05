from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv
import os

from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from passlib.context import CryptContext

load_dotenv('.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = os.environ.get("ALGORITHM", "HS256")
SECRET_KEY = os.environ.get("APP_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("APP_SECRET_KEY is not set in the environment variables")

def create_access_token(subject: str | Any) -> str:
    acess_token_expires_min = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    expire = datetime.now() + timedelta(minutes=int(acess_token_expires_min))
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

