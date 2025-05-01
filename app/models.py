from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey, Boolean, UUID, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base, get_async_session
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.ext.asyncio import AsyncSession


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    username = Column(String(20), unique=True, index=True)
    is_vendor = Column(Boolean, default=False)

    items = relationship("Item", back_populates="vendor")
    rental_requests_sent = relationship(
        "RentalRequest", foreign_keys="[RentalRequest.requester_id]", back_populates="requester")
    rental_requests_received = relationship(
        "RentalRequest", foreign_keys="[RentalRequest.vendor_id]", back_populates="vendor")
    reviews_made = relationship(
        "ItemReview", foreign_keys="[ItemReview.reviewer_id]", back_populates="reviewer")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(BigInteger)
    name = Column(String, index=True)
    price = Column(Float)
    review = Column(Float)
    description = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    vendor_id = Column(UUID, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    vendor = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
    images = relationship(
        "ItemImage", back_populates="item", cascade="all, delete")
    rental_requests = relationship(
        "RentalRequest", back_populates="item", cascade="all, delete")
    reviews = relationship(
        "ItemReview", back_populates="item", cascade="all, delete")

    @property
    def location(self):
        return {"latitude": self.latitude, "longitude": self.longitude}


class ItemReview(Base):
    __tablename__ = "item_reviews"
    id = Column(Integer, primary_key=True, index=True)
    review_details = Column(String)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    reviewer_id = Column(UUID, ForeignKey("users.id"))
    rating = Column(String)

    reviewer = relationship("User", foreign_keys=[
        reviewer_id], back_populates="reviews_made")  # todo
    item = relationship("Item", back_populates="reviews")


class ItemImage(Base):
    __tablename__ = "item_images"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    url = Column(String)

    item = relationship("Item", back_populates="images")


class RentalRequest(Base):
    __tablename__ = "rental_requests"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    requester_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending", nullable=False)

    item = relationship("Item", back_populates="rental_requests")
    requester = relationship("User", foreign_keys=[
                             requester_id], back_populates="rental_requests_sent")
    vendor = relationship("User", foreign_keys=[
                          vendor_id],   back_populates="rental_requests_received")
