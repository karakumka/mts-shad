from pydantic import BaseModel, EmailStr

__all__ = [
    "TokenRequest",
    "TokenResponse"
]

class TokenRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str="bearer"