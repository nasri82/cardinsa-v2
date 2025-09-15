from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.providers.models.provider_network_member_model import ProviderNetworkMember
from uuid import UUID

async def get_network_member_by_id(db: AsyncSession, id: UUID):
    result = await db.execute(select(ProviderNetworkMember).where(ProviderNetworkMember.id == id))
    return result.scalars().first()

async def create_network_member(db: AsyncSession, obj_in: dict):
    db_obj = ProviderNetworkMember(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_network_member(db: AsyncSession, db_obj: ProviderNetworkMember):
    await db.delete(db_obj)
    await db.commit()
