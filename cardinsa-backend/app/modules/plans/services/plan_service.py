# app/modules/plans/services/plan_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_model import Plan
from app.modules.plans.schemas.plan_schema import PlanCreate, PlanUpdate
from app.modules.plans.repositories import plan_repository

async def get_plan(session: AsyncSession, plan_id: UUID) -> Plan | None:
    return await plan_repository.get_plan_by_id(session, plan_id)

async def list_plans(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Plan]:
    return await plan_repository.get_all_plans(session, skip, limit)

async def create_plan(session: AsyncSession, payload: PlanCreate) -> Plan:
    plan = Plan(**payload.dict())
    return await plan_repository.create_plan(session, plan)

async def update_plan(session: AsyncSession, db_plan: Plan, payload: PlanUpdate) -> Plan:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_plan, field, value)
    return await plan_repository.update_plan(session, db_plan)

async def delete_plan(session: AsyncSession, db_plan: Plan) -> None:
    return await plan_repository.delete_plan(session, db_plan)
