from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.providers.models.provider_service_price_model import ProviderServicePrice
from uuid import UUID

async def get_service_price_by_id(db: AsyncSession, id: UUID):
    result = await db.execute(select(ProviderServicePrice).where(ProviderServicePrice.id == id))
    return result.scalars().first()

async def create_service_price(db: AsyncSession, obj_in: dict):
    db_obj = ProviderServicePrice(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_service_price(db: AsyncSession, db_obj: ProviderServicePrice, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_service_price(db: AsyncSession, db_obj: ProviderServicePrice):
    await db.delete(db_obj)
    await db.commit()
