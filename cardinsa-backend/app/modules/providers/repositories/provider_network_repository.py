from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.providers.models.provider_network_model import ProviderNetwork
from uuid import UUID

async def get_provider_network_by_id(db: AsyncSession, id: UUID):
    result = await db.execute(select(ProviderNetwork).where(ProviderNetwork.id == id))
    return result.scalars().first()

async def create_provider_network(db: AsyncSession, obj_in: dict):
    db_obj = ProviderNetwork(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_provider_network(db: AsyncSession, db_obj: ProviderNetwork, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_provider_network(db: AsyncSession, db_obj: ProviderNetwork):
    await db.delete(db_obj)
    await db.commit()
