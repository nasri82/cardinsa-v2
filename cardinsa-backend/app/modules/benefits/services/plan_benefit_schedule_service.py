# app/modules/benefits/services/plan_benefit_schedule_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.benefits.models.plan_benefit_schedule_model import PlanBenefitSchedule
from app.modules.benefits.schemas.plan_benefit_schedule_schema import PlanBenefitScheduleCreate, PlanBenefitScheduleUpdate
from app.modules.benefits.repositories import plan_benefit_schedule_repository

async def list_schedules_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanBenefitSchedule]:
    return await plan_benefit_schedule_repository.get_schedules_by_plan(session, plan_id)

async def get_schedule(session: AsyncSession, schedule_id: UUID) -> PlanBenefitSchedule | None:
    return await plan_benefit_schedule_repository.get_schedule_by_id(session, schedule_id)

async def create_schedule(session: AsyncSession, payload: PlanBenefitScheduleCreate, plan_id: UUID) -> PlanBenefitSchedule:
    schedule = PlanBenefitSchedule(**payload.dict(), plan_id=plan_id)
    return await plan_benefit_schedule_repository.create_schedule(session, schedule)

async def update_schedule(session: AsyncSession, db_schedule: PlanBenefitSchedule, payload: PlanBenefitScheduleUpdate) -> PlanBenefitSchedule:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_schedule, field, value)
    return await plan_benefit_schedule_repository.update_schedule(session, db_schedule)

async def delete_schedule(session: AsyncSession, db_schedule: PlanBenefitSchedule) -> None:
    return await plan_benefit_schedule_repository.delete_schedule(session, db_schedule)
