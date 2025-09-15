from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.demographics.repositories import premium_age_bracket_repository
from app.modules.demographics.models.premium_age_bracket_model import PremiumAgeBracket

async def get_premium_age_bracket(db: AsyncSession, id: UUID) -> PremiumAgeBracket:
    return await premium_age_bracket_repository.get_premium_age_bracket(db, id)

async def get_all_premium_age_brackets(db: AsyncSession):
    return await premium_age_bracket_repository.get_all_premium_age_brackets(db)

async def create_premium_age_bracket(db: AsyncSession, obj_in):
    return await premium_age_bracket_repository.create_premium_age_bracket(db, obj_in.dict())

async def update_premium_age_bracket(db: AsyncSession, db_obj: PremiumAgeBracket, obj_in):
    return await premium_age_bracket_repository.update_premium_age_bracket(db, db_obj, obj_in.dict())

async def delete_premium_age_bracket(db: AsyncSession, db_obj: PremiumAgeBracket):
    return await premium_age_bracket_repository.delete_premium_age_bracket(db, db_obj)
