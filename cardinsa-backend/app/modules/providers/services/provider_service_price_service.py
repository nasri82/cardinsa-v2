from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.providers.repositories import provider_service_price_repository
from uuid import UUID

async def get_service_price(db: AsyncSession, id: UUID):
    return await provider_service_price_repository.get_service_price_by_id(db, id)

async def create_service_price(db: AsyncSession, obj_in):
    return await provider_service_price_repository.create_service_price(db, obj_in.dict())

async def update_service_price(db: AsyncSession, db_obj, obj_in):
    return await provider_service_price_repository.update_service_price(db, db_obj, obj_in.dict())

async def delete_service_price(db: AsyncSession, db_obj):
    return await provider_service_price_repository.delete_service_price(db, db_obj)
