from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.providers.models.provider_model import Provider
from uuid import UUID

async def get_provider_by_id(db: AsyncSession, id: UUID):
    result = await db.execute(select(Provider).where(Provider.id == id))
    return result.scalars().first()

async def create_provider(db: AsyncSession, obj_in: dict):
    db_obj = Provider(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_provider(db: AsyncSession, db_obj: Provider, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_provider(db: AsyncSession, db_obj: Provider):
    await db.delete(db_obj)
    await db.commit()
