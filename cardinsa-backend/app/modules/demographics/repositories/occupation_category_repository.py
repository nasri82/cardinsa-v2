from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.modules.demographics.models.occupation_category_model import OccupationCategory

async def get_occupation_category(db: AsyncSession, id: UUID):
    result = await db.execute(select(OccupationCategory).where(OccupationCategory.id == id))
    return result.scalars().first()

async def get_all_occupation_categories(db: AsyncSession):
    result = await db.execute(select(OccupationCategory))
    return result.scalars().all()

async def create_occupation_category(db: AsyncSession, obj_in: dict):
    obj = OccupationCategory(**obj_in)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def update_occupation_category(db: AsyncSession, db_obj: OccupationCategory, obj_in: dict):
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_occupation_category(db: AsyncSession, db_obj: OccupationCategory):
    await db.delete(db_obj)
    await db.commit()
