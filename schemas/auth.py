from pydantic import BaseModel, EmailStr
from datetime import datetime


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str


class SetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True