from pydantic import BaseModel  # type: ignore

from app_gestao.schemas.user import UserPublic


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    user: UserPublic


class RefreshToken(BaseModel):
    refresh_token: str


class TokenRefresh(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
