from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from datetime import datetime, timezone

router = APIRouter(
    prefix="/v1/api",
    tags=["items"]
)

# Dummy authentication dependency.
# In production, implement proper authentication (e.g., JWT/OAuth2).


def get_current_user(db: Session = Depends(get_db)) -> models.User:
    user = db.query(models.User).first()
    if not user:
        # For demonstration, create a demo vendor user if none exists.
        user = models.User(username="demo_vendor", is_vendor=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/items", response_model=dict)
def get_items(
    page: int = Query(1, description="Page number (must be >= 1)"),
    per_page: int = Query(
        5, description="Number of items per page (must be >= 1)"),
    db: Session = Depends(get_db)
):
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Page and per_page must be positive integers.")

    total_items = db.query(models.Item).count()
    total_pages = (total_items + per_page - 1) // per_page

    offset = (page - 1) * per_page
    db_items = db.query(models.Item).offset(offset).limit(per_page).all()
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
    return JSONResponse(content=response)


@router.get("/items/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    print(item)
    return schemas.Item.model_validate(item)


@router.post("/items/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not registered as a vendor.")

    category = db.query(models.Category).filter(
        models.Category.name == item_data.category.name).first()
    if not category:
        category = models.Category(name=item_data.category.name)
        db.add(category)
        db.commit()
        db.refresh(category)

    new_item = models.Item(
        created_at=int(datetime.now(timezone.fromutc).timestamp() * 1000),
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
    db.commit()
    db.refresh(new_item)

    # Add images
    for url in item_data.images:
        img = models.ItemImage(item_id=new_item.id, url=url)
        db.add(img)
    db.commit()
    db.refresh(new_item)

    return schemas.Item.model_validate(new_item)


@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item_data: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not registered as a vendor.")

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.vendor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item.")

    # Check if the category exists; if not, create it.
    category = db.query(models.Category).filter(
        models.Category.name == item_data.category.name).first()
    if not category:
        category = models.Category(name=item_data.category.name)
        db.add(category)
        db.commit()
        db.refresh(category)

    item.created_at = item_data.created_at
    item.name = item_data.name
    item.price = item_data.price
    item.review = item_data.review
    item.description = item_data.description
    item.latitude = item_data.location.latitude
    item.longitude = item_data.location.longitude
    item.category_id = category.id

    db.query(models.ItemImage).filter(
        models.ItemImage.item_id == item_id).delete()
    for url in item_data.images:
        db.add(models.ItemImage(item_id=item_id, url=url))

    db.commit()
    db.refresh(item)

    return schemas.Item.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not registered as a vendor.")

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item not found")
    if item.vendor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item.")

    db.delete(item)
    db.commit()
    return None
