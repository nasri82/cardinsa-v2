# app/modules/plans/repositories/plan_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_model import Plan
from uuid import UUID

async def get_plan_by_id(session: AsyncSession, plan_id: UUID) -> Plan | None:
    result = await session.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalars().first()

async def get_all_plans(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Plan]:
    result = await session.execute(select(Plan).offset(skip).limit(limit))
    return result.scalars().all()

async def create_plan(session: AsyncSession, plan: Plan) -> Plan:
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan

async def update_plan(session: AsyncSession, db_plan: Plan) -> Plan:
    await session.commit()
    await session.refresh(db_plan)
    return db_plan

async def delete_plan(session: AsyncSession, db_plan: Plan) -> None:
    await session.delete(db_plan)
    await session.commit()
