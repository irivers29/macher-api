from pydantic import BaseModel, ConfigDict, validator
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from typing import List
from datetime import datetime
from typing import Optional
from uuid import UUID

# TODO: change ids to uuid
# TODO: rework inheritance structure of schemas


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


class RentalRequestCreate(BaseModel):
    item_id: int
    message: Optional[str]
    start_time: datetime
    end_time: datetime

    @validator("end_time")  # TODO: migrate to non-deprecated field_validator
    def end_must_be_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class RentalRequestResponse(BaseModel):
    id: int
    item_id: int
    requester_id: UUID
    vendor_id: UUID
    message: Optional[str]
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        orm_mode = True


class ProductAvailabilityBase(BaseModel):
    start_time: datetime
    end_time: datetime


class ProductAvailabilityCreate(ProductAvailabilityBase):
    product_id: int


class ProductAvailability(ProductAvailabilityBase):
    id: int
    product_id: int
    vendor_id: int

    class Config:
        orm_mode = True


class BookingBase(BaseModel):
    availability_id: int
    user_id: int


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    booked_at: datetime

    class Config:
        orm_mode = True


class ReviewCreate(BaseModel):
    item_id: int
    review_details: str
    rating: int

    @validator("rating")
    def validate_rating(cls, v, values):
        if v < 1 or v > 5:
            raise ValueError("the rating needs to be between 1 and 5")
