from pydantic import BaseModel, ConfigDict
from typing import List


class UserBase(BaseModel):
    username: str
    is_vendor: bool


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


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
    vendor: User
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
