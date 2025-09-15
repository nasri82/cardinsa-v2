from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.demographics.repositories import age_bracket_repository
from app.modules.demographics.models.age_bracket_model import AgeBracket

async def get_age_bracket(db: AsyncSession, id: UUID) -> AgeBracket:
    return await age_bracket_repository.get_age_bracket(db, id)

async def get_all_age_brackets(db: AsyncSession):
    return await age_bracket_repository.get_all_age_brackets(db)

async def create_age_bracket(db: AsyncSession, obj_in):
    return await age_bracket_repository.create_age_bracket(db, obj_in.dict())

async def update_age_bracket(db: AsyncSession, db_obj: AgeBracket, obj_in):
    return await age_bracket_repository.update_age_bracket(db, db_obj, obj_in.dict())

async def delete_age_bracket(db: AsyncSession, db_obj: AgeBracket):
    return await age_bracket_repository.delete_age_bracket(db, db_obj)
