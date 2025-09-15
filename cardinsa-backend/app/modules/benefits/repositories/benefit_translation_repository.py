# app/modules/benefits/repositories/benefit_translation_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.benefits.models.benefit_translation_model import BenefitTranslation
from uuid import UUID

async def get_translations_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitTranslation]:
    result = await session.execute(
        select(BenefitTranslation).where(BenefitTranslation.schedule_id == schedule_id)
    )
    return result.scalars().all()

async def create_translation(session: AsyncSession, translation: BenefitTranslation) -> BenefitTranslation:
    session.add(translation)
    await session.commit()
    await session.refresh(translation)
    return translation

async def delete_translation(session: AsyncSession, translation: BenefitTranslation) -> None:
    await session.delete(translation)
    await session.commit()
