# app/modules/benefits/repositories/plan_benefit_schedule_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.benefits.models.plan_benefit_schedule_model import PlanBenefitSchedule
from uuid import UUID

async def get_schedules_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanBenefitSchedule]:
    result = await session.execute(
        select(PlanBenefitSchedule).where(PlanBenefitSchedule.plan_id == plan_id)
    )
    return result.scalars().all()

async def get_schedule_by_id(session: AsyncSession, schedule_id: UUID) -> PlanBenefitSchedule | None:
    result = await session.execute(
        select(PlanBenefitSchedule).where(PlanBenefitSchedule.id == schedule_id)
    )
    return result.scalars().first()

async def create_schedule(session: AsyncSession, schedule: PlanBenefitSchedule) -> PlanBenefitSchedule:
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule

async def update_schedule(session: AsyncSession, db_schedule: PlanBenefitSchedule) -> PlanBenefitSchedule:
    await session.commit()
    await session.refresh(db_schedule)
    return db_schedule

async def delete_schedule(session: AsyncSession, db_schedule: PlanBenefitSchedule) -> None:
    await session.delete(db_schedule)
    await session.commit()
