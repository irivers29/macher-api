# app/routers/reviews.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func
from app.models import User, ItemReview
from app.schemas import ReviewCreate
from app.database import get_async_session
from app.users import active_user

router = APIRouter(
    prefix="/v1/api",
    tags=["reviews"]
)


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def post_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(active_user)
):
    # TODO: think if we want to review the product or the vendor

    # if current_user.id == review_data.vendor_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot review yourself."
    # )

    # # Optional: Check if user already reviewed this vendor
    # existing = await db.execute(
    #     select(ItemReview).where(
    #         ItemReview.reviewer_id == current_user.id,
    #         ItemReview.vendor_id == review_data.vendor_id
    #     )
    # )
    # if existing.scalar_one_or_none():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="You have already reviewed this vendor."
    #     )

    # TODO
    review = ItemReview(
        reviewer_id=current_user.id,
        item_id=review_data.item_id,
        rating=review_data.rating,
        review_details=review_data.review_details
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/reviews/item/{item_id}")
async def get_reviews_for_vendor(
    item_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    stmt = select(ItemReview).where(ItemReview.item_id == item_id)
    result = await db.execute(stmt)
    db_items = result.scalars().all()
    return db_items


# @router.get("/reviews/vendor/{vendor_id}/average-rating")
# async def get_vendor_rating(
#     vendor_id: int,
#     db: AsyncSession = Depends(get_async_session)
# ):
#     stmt = select(func.avg(ItemReview.rating)).where(
#         ItemReview.vendor_id == vendor_id)
#     result = await db.execute(stmt)
#     avg_rating = result.scalar()
#     return {"vendor_id": vendor_id, "average_rating": round(avg_rating or 0, 2)}
