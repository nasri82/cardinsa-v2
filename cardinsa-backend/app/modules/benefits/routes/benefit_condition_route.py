# app/modules/benefits/routes/benefit_condition_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.benefits.schemas.benefit_condition_schema import BenefitConditionCreate, BenefitConditionOut
from app.modules.benefits.services import benefit_condition_service

router = APIRouter(prefix="/benefit-schedules/{schedule_id}/conditions", tags=["Benefit Conditions"])

@router.get("/", response_model=list[BenefitConditionOut])
async def list_conditions(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "view"))
):
    return await benefit_condition_service.list_conditions_by_schedule(session, schedule_id)

@router.post("/", response_model=BenefitConditionOut)
async def create_condition(
    schedule_id: UUID,
    payload: BenefitConditionCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "create"))
):
    return await benefit_condition_service.create_condition(session, payload, schedule_id)
