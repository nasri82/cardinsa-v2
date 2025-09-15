# app/modules/benefits/routes/benefit_translation_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.benefits.schemas.benefit_translation_schema import BenefitTranslationCreate, BenefitTranslationOut
from app.modules.benefits.services import benefit_translation_service

router = APIRouter(prefix="/benefit-schedules/{schedule_id}/translations", tags=["Benefit Translations"])

@router.get("/", response_model=list[BenefitTranslationOut])
async def list_translations(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "view"))
):
    return await benefit_translation_service.list_translations_by_schedule(session, schedule_id)

@router.post("/", response_model=BenefitTranslationOut)
async def create_translation(
    schedule_id: UUID,
    payload: BenefitTranslationCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "create"))
):
    return await benefit_translation_service.create_translation(session, payload, schedule_id)
