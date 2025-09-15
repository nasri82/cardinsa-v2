from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.providers.repositories import provider_type_repository
from uuid import UUID

async def get_provider_type(db: AsyncSession, id: UUID):
    return await provider_type_repository.get_provider_type_by_id(db, id)

async def create_provider_type(db: AsyncSession, obj_in):
    return await provider_type_repository.create_provider_type(db, obj_in.dict())

async def update_provider_type(db: AsyncSession, db_obj, obj_in):
    return await provider_type_repository.update_provider_type(db, db_obj, obj_in.dict())

async def delete_provider_type(db: AsyncSession, db_obj):
    return await provider_type_repository.delete_provider_type(db, db_obj)
