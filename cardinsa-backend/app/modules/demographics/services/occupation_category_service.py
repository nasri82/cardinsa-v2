from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.demographics.repositories import occupation_category_repository
from app.modules.demographics.models.occupation_category_model import OccupationCategory

async def get_occupation_category(db: AsyncSession, id: UUID) -> OccupationCategory:
    return await occupation_category_repository.get_occupation_category(db, id)

async def get_all_occupation_categories(db: AsyncSession):
    return await occupation_category_repository.get_all_occupation_categories(db)

async def create_occupation_category(db: AsyncSession, obj_in):
    return await occupation_category_repository.create_occupation_category(db, obj_in.dict())

async def update_occupation_category(db: AsyncSession, db_obj: OccupationCategory, obj_in):
    return await occupation_category_repository.update_occupation_category(db, db_obj, obj_in.dict())

async def delete_occupation_category(db: AsyncSession, db_obj: OccupationCategory):
    return await occupation_category_repository.delete_occupation_category(db, db_obj)
