# # models.py
# from sqlalchemy import Column, Integer, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from datetime import datetime

# class ProductAvailability(Base):
#     __tablename__ = 'product_availabilities'

#     id = Column(Integer, primary_key=True, index=True)
#     product_id = Column(Integer, ForeignKey('items.id'), nullable=False)
#     start_time = Column(DateTime, nullable=False)
#     end_time = Column(DateTime, nullable=False)
#     vendor_id = Column(Integer, ForeignKey('users.id'), nullable=False)

#     product = relationship('Item', back_populates='availabilities')
#     vendor = relationship('User', back_populates='availabilities')


# class Booking(Base):
#     __tablename__ = 'bookings'

#     id = Column(Integer, primary_key=True, index=True)
#     availability_id = Column(Integer, ForeignKey('product_availabilities.id'), nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     booked_at = Column(DateTime, default=datetime.utcnow)

#     availability = relationship('ProductAvailability', back_populates='bookings')
#     user = relationship('User', back_populates='bookings')