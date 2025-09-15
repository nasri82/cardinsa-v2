# app/modules/plans/services/plan_exclusion_link_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_exclusion_link_model import PlanExclusionLink
from app.modules.plans.schemas.plan_exclusion_link_schema import PlanExclusionLinkCreate
from app.modules.plans.repositories import plan_exclusion_link_repository

async def list_exclusions_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanExclusionLink]:
    return await plan_exclusion_link_repository.get_exclusions_by_plan(session, plan_id)

async def create_exclusion_link(session: AsyncSession, payload: PlanExclusionLinkCreate, plan_id: UUID) -> PlanExclusionLink:
    link = PlanExclusionLink(**payload.dict(), plan_id=plan_id)
    return await plan_exclusion_link_repository.create_exclusion_link(session, link)
