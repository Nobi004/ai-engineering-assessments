from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings
import asyncio

async_engine = create_async_engine(settings.db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session