from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.modules.demographics.models.premium_age_bracket_model import PremiumAgeBracket

async def get_premium_age_bracket(db: AsyncSession, id: UUID):
    result = await db.execute(select(PremiumAgeBracket).where(PremiumAgeBracket.id == id))
    return result.scalars().first()

async def get_all_premium_age_brackets(db: AsyncSession):
    result = await db.execute(select(PremiumAgeBracket))
    return result.scalars().all()

async def create_premium_age_bracket(db: AsyncSession, obj_in: dict):
    obj = PremiumAgeBracket(**obj_in)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def update_premium_age_bracket(db: AsyncSession, db_obj: PremiumAgeBracket, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_premium_age_bracket(db: AsyncSession, db_obj: PremiumAgeBracket):
    await db.delete(db_obj)
    await db.commit()
