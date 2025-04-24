# from pydantic import BaseModel
# from datetime import datetime
# from typing import List, Optional


# class ProductAvailabilityBase(BaseModel):
#     start_time: datetime
#     end_time: datetime


# class ProductAvailabilityCreate(ProductAvailabilityBase):
#     product_id: int


# class ProductAvailability(ProductAvailabilityBase):
#     id: int
#     product_id: int
#     vendor_id: int

#     class Config:
#         orm_mode = True


# class BookingBase(BaseModel):
#     availability_id: int
#     user_id: int


# class BookingCreate(BookingBase):
#     pass


# class Booking(BookingBase):
#     id: int
#     booked_at: datetime

#     class Config:
#         orm_mode = True
