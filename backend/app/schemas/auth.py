from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserRead


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginResponse(Token):
    user: UserRead


class RefreshTokenRequest(BaseModel):
    refresh_token: str
