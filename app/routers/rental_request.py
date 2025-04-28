from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from sqlalchemy import UUID

from app.database import get_async_session
from app.models import RentalRequest as RentalRequestORM, Item
from app.schemas import RentalRequestCreate, RentalRequestResponse
from app.users import fastapi_users
from app.models import User as UserModel

router = APIRouter(prefix="/v1/api", tags=["rental requests"])

current_user = fastapi_users.current_user()


@router.post("/rental_requests", response_model=RentalRequestResponse)
async def create_rental_request(
    request_data: RentalRequestCreate,
    response: Response,
    user: UserModel = Depends(current_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Validate item exists
    result = await db.execute(select(Item).where(Item.id == request_data.item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item.vendor_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot request your own item")

    overlap_q = (
        select(RentalRequestORM)
        .where(
            RentalRequestORM.item_id == item.id,
            RentalRequestORM.status == "accepted",
            RentalRequestORM.start_time < request_data.end_time,
        )
    )

    conflict = await db.execute(overlap_q)
    if conflict.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item is already booked for some or all of that period",
        )

    new_req = RentalRequestORM(
        item_id=request_data.item_id,
        requester_id=user.id,
        vendor_id=item.vendor_id,
        message=request_data.message,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
    )

    db.add(new_req)
    await db.commit()
    await db.refresh(new_req)

    response.headers["Location"] = f"/rental_requests/{new_req.id}"
    return new_req


@router.get("/rental_requests", response_model=List[RentalRequestResponse])
async def get_my_rental_requests(
    user: UserModel = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # TODO: add flag to allow the frontend to get only the requests that are assigned to him as a vendor or that allows him to see only the request that he has made
    result = await session.execute(
        select(RentalRequestORM)
        .where((RentalRequestORM.requester_id == user.id) | (RentalRequestORM.vendor_id == user.id))
        .options()
    )
    return result.scalars().all()


@router.patch("/rental_requests/{request_id}/status", response_model=RentalRequestResponse)
# TODO: update this to allow a user to cancel a request if not already accepted
async def update_request_status(
    request_id: int,
    status: str,
    user: UserModel = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(RentalRequestORM).where(RentalRequestORM.id == request_id))
    rental_request = result.scalar_one_or_none()

    if rental_request is None:
        raise HTTPException(status_code=404, detail="Rental request not found")

    if rental_request.vendor_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this request")

    if status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    rental_request.status = status
    await session.commit()
    await session.refresh(rental_request)
    return rental_request
