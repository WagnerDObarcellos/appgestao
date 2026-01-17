from pydantic import BaseModel  # type: ignore


class Message(BaseModel):
    message: str


class FilterPage(BaseModel):
    skip: int = 0
    limit: int = 100
