from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # or joinedload
from datetime import datetime, timezone

from app import models, schemas
from app.database import get_async_session  # Use your async session generator
from app.users import active_user

router = APIRouter(
    prefix="/v1/api",
    tags=["items"]
)


@router.get("/items", response_model=dict)
async def get_items(
    page: int = Query(1, description="Page number (must be >= 1)"),
    per_page: int = Query(
        5, description="Number of items per page (must be >= 1)"),
    db: AsyncSession = Depends(get_async_session)
):
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and per_page must be positive integers."
        )

    # Count total items
    count_stmt = select(func.count(models.Item.id))
    count_result = await db.execute(count_stmt)
    total_items = count_result.scalar() or 0
    total_pages = (total_items + per_page - 1) // per_page

    offset = (page - 1) * per_page
    stmt = (
        select(models.Item)
        .options(
            selectinload(models.Item.vendor),
            selectinload(models.Item.category),
            selectinload(models.Item.images)
        )
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    db_items = result.scalars().all()

    # For debugging purposes
    for item in db_items:
        print(item)

    items_data = [schemas.Item.model_validate(
        item).model_dump() for item in db_items]

    response = {
        "itemsReceived": len(items_data),
        "curPage": page,
        "nextPage": page + 1 if page < total_pages else None,
        "prevPage": page - 1 if page > 1 else None,
        "offset": offset,
        "itemsTotal": total_items,
        "pageTotal": total_pages,
        "items": items_data
    }
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/items/{item_id}", response_model=schemas.Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_async_session)):
    stmt = (
        select(models.Item).filter(models.Item.id == item_id)
        .options(
            selectinload(models.Item.vendor),
            selectinload(models.Item.category),
            selectinload(models.Item.images)
        )
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return schemas.Item.model_validate(item)


@router.post("/items/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: schemas.ItemCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)  # <-- Use active_user
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a vendor."
        )

    # Check for existing category
    stmt = select(models.Category).filter(
        models.Category.name == item_data.category.name)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        category = models.Category(name=item_data.category.name)
        db.add(category)
        await db.commit()
        await db.refresh(category)

    new_item = models.Item(
        created_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        name=item_data.name,
        price=item_data.price,
        review=0,
        description=item_data.description,
        latitude=item_data.location.latitude,
        longitude=item_data.location.longitude,
        vendor_id=current_user.id,
        category_id=category.id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # Add images
    for url in item_data.images:
        img = models.ItemImage(item_id=new_item.id, url=url)
        db.add(img)
    await db.commit()

    stmt = select(models.Item).options(
        selectinload(models.Item.vendor),
        selectinload(models.Item.images)
    ).filter(models.Item.id == new_item.id)
    result = await db.execute(stmt)
    new_item = result.scalar_one()

    return schemas.Item.model_validate(new_item)


# should i add patch method?
@router.put("/items/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int,
    item_data: schemas.ItemCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)  # <-- Use active_user
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a vendor."
        )

    # Fetch the item
    stmt = (
        select(models.Item)
        .options(
            selectinload(models.Item.vendor),
            selectinload(models.Item.images)
        )
        .filter(models.Item.id == item_id)
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    if item.vendor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item."
        )

    # Fetch or create category
    stmt = select(models.Category).filter(
        models.Category.name == item_data.category.name)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        category = models.Category(name=item_data.category.name)
        db.add(category)
        await db.commit()
        await db.refresh(category)

    # Update item fields
    item.name = item_data.name
    item.price = item_data.price
    item.description = item_data.description
    item.latitude = item_data.location.latitude
    item.longitude = item_data.location.longitude
    item.category_id = category.id

    # Delete existing images using an async delete query
    del_stmt = delete(models.ItemImage).where(
        models.ItemImage.item_id == item_id)
    await db.execute(del_stmt)

    # Insert new images
    for url in item_data.images:
        db.add(models.ItemImage(item_id=item_id, url=url))

    await db.commit()
    await db.refresh(item)

    return schemas.Item.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(active_user)  # <-- Use active_user
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a vendor."
        )

    stmt = select(models.Item).filter(models.Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item not found"
        )
    if item.vendor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item."
        )

    await db.delete(item)
    await db.commit()
    return None
