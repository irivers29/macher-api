from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI

engine = create_async_engine(SQLALCHEMY_DATABASE_URI)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
