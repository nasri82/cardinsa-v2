from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.providers.repositories import provider_network_member_repository
from uuid import UUID

async def get_network_member(db: AsyncSession, id: UUID):
    return await provider_network_member_repository.get_network_member_by_id(db, id)

async def create_network_member(db: AsyncSession, obj_in):
    return await provider_network_member_repository.create_network_member(db, obj_in.dict())

async def delete_network_member(db: AsyncSession, db_obj):
    return await provider_network_member_repository.delete_network_member(db, db_obj)
