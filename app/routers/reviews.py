# app/routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app import models, schemas
from app.database import get_async_session
from app.users import active_user

router = APIRouter(
    prefix="/v1/api/reviews",
    tags=["reviews"]
)

@router.post("/", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
async def post_review(
    review_data: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)
):
    if current_user.id == review_data.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot review yourself."
        )

    # Optional: Check if user already reviewed this vendor
    existing = await db.execute(
        select(models.Review).where(
            models.Review.reviewer_id == current_user.id,
            models.Review.vendor_id == review_data.vendor_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this vendor."
        )

    review = models.Review(
        reviewer_id=current_user.id,
        vendor_id=review_data.vendor_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review

@router.get("/vendor/{vendor_id}", response_model=list[schemas.ReviewOut])
async def get_reviews_for_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    stmt = select(models.Review).where(models.Review.vendor_id == vendor_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/vendor/{vendor_id}/average-rating")
async def get_vendor_rating(
    vendor_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    stmt = select(func.avg(models.Review.rating)).where(models.Review.vendor_id == vendor_id)
    result = await db.execute(stmt)
    avg_rating = result.scalar()
    return {"vendor_id": vendor_id, "average_rating": round(avg_rating or 0, 2)}
