from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@gmail.com")
    password: str = Field(..., min_length=6)
    address: str = Field(..., example="123 Main St, Anytown, USA")


class UserUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    address: str


class GameCreate(BaseModel):
    name: str = Field(..., example="Super Mario Bros.")
    publisher: str = Field(..., example="Nintendo")
    year_published: int = Field(..., example=1985)
    system: str = Field(..., example="NES")
    condition: str = Field(..., example="Good")
    previous_owners: Optional[int] = Field(0, example=2)


class GameUpdate(BaseModel):
    name: Optional[str]
    publisher: Optional[str]
    year_published: Optional[int]
    system: Optional[str]
    condition: Optional[str]
    previous_owners: Optional[int]


class GameResponse(BaseModel):
    id: str
    name: str
    publisher: str
    year_published: int
    system: str
    condition: str
    previous_owners: Optional[int]
    owner_id: str
