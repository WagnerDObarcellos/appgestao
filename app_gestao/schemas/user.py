from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr  # type: ignore


# 👉 entrada (POST /users)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# 👉 saída pública
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


# 👉 lista
class UserList(BaseModel):
    users: list[UserPublic]


# 👉 update
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
