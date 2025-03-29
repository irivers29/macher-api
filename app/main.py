from fastapi import FastAPI
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, fastapi_users
from app.database import async_session_maker, create_db_and_tables
from app.routers import items
from sqlalchemy import select, func
from app import models

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await populate_db()
    yield

app = FastAPI(title="My Macher App", lifespan=lifespan)

# Include routers
app.include_router(items.router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Macher app!"}


async def populate_db():
    async with async_session_maker() as db:
        # Check if any items exist
        stmt = select(func.count(models.Item.id))
        result = await db.execute(stmt)
        total_items = result.scalar() or 0

        if total_items == 0:
            sample_data = [
                {
                    "id": 25,
                    "created_at": 1729684358920,
                    "name": "Drill",
                    "location": {"latitude": "48.1499776", "longitude": "11.5642907"},
                    "vendor": "Macher Box",
                    "vendor_name": "Peter Whitmore",
                    "price": 32,
                    "category": "tools",
                    "image": [
                        "https://forum.englishforlife.mk/sites/default/assets/img/attachments/5874cff703658.jpg",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inalámbrico.jpg?s=612x612",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 3.5,
                    "description": "A high-quality drill perfect for all household and DIY tasks."
                },
                {
                    "id": 26,
                    "created_at": 1729684358921,
                    "name": "Toolbox",
                    "location": {"latitude": "48.1514132", "longitude": "11.5598136"},
                    "vendor": "Macher Box",
                    "vendor_name": "Sarah Connor",
                    "price": 25,
                    "category": "tools",
                    "image": [
                        "https://i.pinimg.com/236x/a9/58/59/a9585926d0dab1f0bac3aa734772d79c.jpg",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.2,
                    "description": "A compact and durable toolbox containing essential tools."
                },
                {
                    "id": 27,
                    "created_at": 1729684358923,
                    "name": "Cooking Machine",
                    "location": {"latitude": "48.1511432", "longitude": "11.5587717"},
                    "vendor": "Private",
                    "vendor_name": "John Chef",
                    "price": 80,
                    "category": "kitchen appliances",
                    "image": [
                        "https://babadada.com/images/topics/tools_big.png",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.5,
                    "description": "A versatile cooking machine suitable for all types of recipes."
                },
                {
                    "id": 28,
                    "created_at": 1729684358924,
                    "name": "Projector",
                    "location": {"latitude": "48.1532989", "longitude": "11.5603207"},
                    "vendor": "Shop",
                    "vendor_name": "Emily Bright",
                    "price": 50,
                    "category": "electronics",
                    "image": [
                        "https://babadada.com/images/topics/tools_big.png",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.8,
                    "description": "A high-definition projector ideal for home theater setups."
                },
                {
                    "id": 29,
                    "created_at": 1729684358925,
                    "name": "Ladder",
                    "location": {"latitude": "48.1500001", "longitude": "11.5500002"},
                    "vendor": "Shop",
                    "vendor_name": "David Heights",
                    "price": 20,
                    "category": "tools",
                    "image": [
                        "https://babadada.com/images/topics/tools_big.png",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.0,
                    "description": "A sturdy ladder for indoor and outdoor use."
                },
                {
                    "id": 30,
                    "created_at": 1729684358926,
                    "name": "Vacuum Cleaner",
                    "location": {"latitude": "48.1600001", "longitude": "11.5700002"},
                    "vendor": "Private",
                    "vendor_name": "Alice Mop",
                    "price": 40,
                    "category": "cleaning appliances",
                    "image": [
                        "https://babadada.com/images/topics/tools_big.png",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.7,
                    "description": "A powerful and compact vacuum cleaner for daily use."
                },
                {
                    "id": 31,
                    "created_at": 1729684358927,
                    "name": "Power Washerthisisaverylongfasdfasd",
                    "location": {"latitude": "48.1554321", "longitude": "11.5656789"},
                    "vendor": "Private",
                    "vendor_name": "Jack Wash",
                    "price": 60,
                    "category": "cleaning appliances",
                    "image": [
                        "https://babadada.com/images/topics/tools_big.png",
                        "https://media.gettyimages.com/id/184294297/es/foto/atornillador-inal%C3%A1mbrico.jpg?s=612x612&w=gi&k=20&c=RAbORwWPcgV0ChBoFbGyrBWPIkWmWTKn-aL66HftMBY=",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_-LzpQ-19ElzLPBDFAI9ROma3v3hOGIADMA&s",
                        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcQyJybDwH3k_ZhvedIhOhXQgsbT_dNgOoQ&s"
                    ],
                    "review": 4.3,
                    "description": "An efficient power washer for cleaning patios, driveways, and more."
                }
            ]

            for data in sample_data:
                # Check or create vendor
                stmt = select(models.User).filter(
                    models.User.username == data["vendor_name"])
                result = await db.execute(stmt)
                vendor = result.scalar_one_or_none()
                if not vendor:
                    vendor = models.User(
                        username=data["vendor_name"],
                        is_vendor=True,
                        email=generate_email(data["vendor_name"]),
                        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$9ufNT3/+y6CRd5QHK7s7iQ$VC5Rx2MUW16QtKPtyMx/Vgzue9GaQmZjq86rlQAwMqs",
                        is_verified=True
                    )
                    db.add(vendor)
                    await db.commit()
                    await db.refresh(vendor)

                # Check or create category
                stmt = select(models.Category).filter(
                    models.Category.name == data["category"])
                result = await db.execute(stmt)
                category = result.scalar_one_or_none()
                if not category:
                    category = models.Category(name=data["category"])
                    db.add(category)
                    await db.commit()
                    await db.refresh(category)

                latitude = data.get("location", {}).get("latitude")
                longitude = data.get("location", {}).get("longitude")

                # Create the item
                item = models.Item(
                    id=data["id"],
                    created_at=data["created_at"],
                    name=data["name"],
                    price=data["price"],
                    review=data["review"],
                    description=data["description"],
                    latitude=latitude,
                    longitude=longitude,
                    vendor_id=vendor.id,
                    category_id=category.id
                )
                db.add(item)
                await db.commit()
                await db.refresh(item)

                # Add associated images
                for image_url in data["image"]:
                    item_image = models.ItemImage(
                        item_id=item.id, url=image_url)
                    db.add(item_image)
                await db.commit()


def generate_email(username: str) -> str:
    return username.lower().replace(" ", ".") + "@example.com"
