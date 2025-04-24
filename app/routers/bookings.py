from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_async_session
from app import models, schemas
from app.users import active_user
from datetime import datetime

router = APIRouter(
    prefix="/v1/api",
    tags=["bookings"]
)

# Create availability for a product (for vendors)
@router.post("/availability/", response_model=schemas.ProductAvailability)
async def create_availability(
    availability_data: schemas.ProductAvailabilityCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a vendor."
        )

    # Create the availability slot
    new_availability = models.ProductAvailability(
        product_id=availability_data.product_id,
        start_time=availability_data.start_time,
        end_time=availability_data.end_time,
        vendor_id=current_user.id
    )
    db.add(new_availability)
    await db.commit()
    await db.refresh(new_availability)

    return schemas.ProductAvailability.from_orm(new_availability)


# Get all availabilities for a specific item
@router.get("/availability/{item_id}", response_model=List[schemas.ProductAvailability])
async def get_product_availabilities(
    item_id: int, db: AsyncSession = Depends(get_async_session)
):
    stmt = select(models.ProductAvailability).filter(models.ProductAvailability.product_id == item_id)
    result = await db.execute(stmt)
    availabilities = result.scalars().all()

    return [schemas.ProductAvailability.from_orm(a) for a in availabilities]


# Create a booking for an available time slot
@router.post("/bookings/", response_model=schemas.Booking)
async def create_booking(
    booking_data: schemas.BookingCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)
):
    # Ensure the availability exists
    stmt = select(models.ProductAvailability).filter(models.ProductAvailability.id == booking_data.availability_id)
    result = await db.execute(stmt)
    availability = result.scalar_one_or_none()
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")

    # Ensure the user is not booking their own product
    if availability.vendor_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot book your own product")

    # Check if the slot is already booked
    stmt = select(models.Booking).filter(models.Booking.availability_id == booking_data.availability_id)
    result = await db.execute(stmt)
    existing_booking = result.scalar_one_or_none()
    if existing_booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This slot is already booked")

    # Create the booking
    new_booking = models.Booking(
        availability_id=booking_data.availability_id,
        user_id=current_user.id
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    return schemas.Booking.from_orm(new_booking)
