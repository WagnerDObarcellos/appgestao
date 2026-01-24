from pydantic import BaseModel  # type: ignore


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str
