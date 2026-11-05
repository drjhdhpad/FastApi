from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    contact_number: str | None = Field(default=None, max_length=30)
    balance: int = Field(default=0, ge=0)


class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    contact_number: str | None = Field(default=None, max_length=30)
    birth_date: datetime
    balance: int = Field(default=0, ge=0)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    contact_number: str | None
    balance: int
