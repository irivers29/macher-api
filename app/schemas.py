from pydantic import BaseModel, ConfigDict
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from typing import List



class UserRead(BaseUser):
    username: str


class UserCreate(BaseUserCreate):
    username: str
    is_vendor: bool


class UserUpdate(BaseUserUpdate):
    username: str
    is_vendor: bool


class CategoryBase(BaseModel):
    name: str


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemImage(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(from_attributes=True)


class Location(BaseModel):
    latitude: str
    longitude: str


class ItemBase(BaseModel):
    created_at: int
    name: str
    price: float
    review: float
    description: str
    location: Location


class Item(ItemBase):
    id: int
    vendor: UserRead
    category: Category
    images: List[ItemImage]

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    name: str
    price: float
    description: str
    location: Location  # use the location of the user?
    category: CategoryBase
    images: List[str]
