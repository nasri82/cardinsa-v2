# app/modules/benefits/services/benefit_translation_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.benefits.models.benefit_translation_model import BenefitTranslation
from app.modules.benefits.schemas.benefit_translation_schema import BenefitTranslationCreate
from app.modules.benefits.repositories import benefit_translation_repository

async def list_translations_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitTranslation]:
    return await benefit_translation_repository.get_translations_by_schedule(session, schedule_id)

async def create_translation(session: AsyncSession, payload: BenefitTranslationCreate, schedule_id: UUID) -> BenefitTranslation:
    translation = BenefitTranslation(**payload.dict(), schedule_id=schedule_id)
    return await benefit_translation_repository.create_translation(session, translation)

async def delete_translation(session: AsyncSession, translation: BenefitTranslation) -> None:
    return await benefit_translation_repository.delete_translation(session, translation)
