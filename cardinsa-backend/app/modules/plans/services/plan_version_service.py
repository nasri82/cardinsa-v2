# app/modules/plans/services/plan_version_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_version_model import PlanVersion
from app.modules.plans.schemas.plan_version_schema import PlanVersionCreate
from app.modules.plans.repositories import plan_version_repository

async def list_versions_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanVersion]:
    return await plan_version_repository.get_versions_by_plan(session, plan_id)

async def create_version(session: AsyncSession, payload: PlanVersionCreate, plan_id: UUID) -> PlanVersion:
    version = PlanVersion(**payload.dict(), plan_id=plan_id)
    return await plan_version_repository.create_version(session, version)

async def set_current_version(session: AsyncSession, plan_id: UUID, version_id: UUID) -> None:
    return await plan_version_repository.set_current_version(session, plan_id, version_id)
