from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    is_vendor = Column(Boolean, default=False)
    # hashed_password and other auth fields would be added in a real app: todo

    items = relationship("Item", back_populates="vendor")


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
    review = Column(Float)  # create a table for reviews
    description = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    vendor_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    vendor = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
    images = relationship(
        "ItemImage", back_populates="item", cascade="all, delete")

    @property
    def location(self):
        return {"latitude": self.latitude, "longitude": self.longitude}


class ItemImage(Base):
    __tablename__ = "item_images"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    url = Column(String)

    item = relationship("Item", back_populates="images")
