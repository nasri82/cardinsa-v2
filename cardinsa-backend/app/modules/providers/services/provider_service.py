from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.providers.repositories import provider_repository
from uuid import UUID

async def get_provider(db: AsyncSession, id: UUID):
    return await provider_repository.get_provider_by_id(db, id)

async def create_provider(db: AsyncSession, obj_in):
    return await provider_repository.create_provider(db, obj_in.dict())

async def update_provider(db: AsyncSession, db_obj, obj_in):
    return await provider_repository.update_provider(db, db_obj, obj_in.dict())

async def delete_provider(db: AsyncSession, db_obj):
    return await provider_repository.delete_provider(db, db_obj)
