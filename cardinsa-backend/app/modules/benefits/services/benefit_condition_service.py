# app/modules/benefits/services/benefit_condition_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.benefits.models.benefit_condition_model import BenefitCondition
from app.modules.benefits.schemas.benefit_condition_schema import BenefitConditionCreate
from app.modules.benefits.repositories import benefit_condition_repository

async def list_conditions_by_schedule(session: AsyncSession, schedule_id: UUID) -> list[BenefitCondition]:
    return await benefit_condition_repository.get_conditions_by_schedule(session, schedule_id)

async def create_condition(session: AsyncSession, payload: BenefitConditionCreate, schedule_id: UUID) -> BenefitCondition:
    condition = BenefitCondition(**payload.dict(), schedule_id=schedule_id)
    return await benefit_condition_repository.create_condition(session, condition)

async def delete_condition(session: AsyncSession, condition: BenefitCondition) -> None:
    return await benefit_condition_repository.delete_condition(session, condition)
