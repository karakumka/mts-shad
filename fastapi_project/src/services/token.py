import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from src.configurations.settings import settings

__all__ = ["create_access_token", "decode_access_token"]


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        return payload
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")