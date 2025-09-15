from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.providers.repositories import provider_network_repository
from uuid import UUID

async def get_provider_network(db: AsyncSession, id: UUID):
    return await provider_network_repository.get_provider_network_by_id(db, id)

async def create_provider_network(db: AsyncSession, obj_in):
    return await provider_network_repository.create_provider_network(db, obj_in.dict())

async def update_provider_network(db: AsyncSession, db_obj, obj_in):
    return await provider_network_repository.update_provider_network(db, db_obj, obj_in.dict())

async def delete_provider_network(db: AsyncSession, db_obj):
    return await provider_network_repository.delete_provider_network(db, db_obj)
