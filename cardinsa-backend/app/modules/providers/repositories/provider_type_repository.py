from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.providers.models.provider_type_model import ProviderType
from uuid import UUID

async def get_provider_type_by_id(db: AsyncSession, id: UUID):
    result = await db.execute(select(ProviderType).where(ProviderType.id == id))
    return result.scalars().first()

async def create_provider_type(db: AsyncSession, obj_in: dict):
    db_obj = ProviderType(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_provider_type(db: AsyncSession, db_obj: ProviderType, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_provider_type(db: AsyncSession, db_obj: ProviderType):
    await db.delete(db_obj)
    await db.commit()
