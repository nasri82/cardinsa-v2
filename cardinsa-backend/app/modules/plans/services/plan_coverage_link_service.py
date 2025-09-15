# app/modules/plans/services/plan_coverage_link_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_coverage_link_model import PlanCoverageLink
from app.modules.plans.schemas.plan_coverage_link_schema import PlanCoverageLinkCreate
from app.modules.plans.repositories import plan_coverage_link_repository

async def list_coverages_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanCoverageLink]:
    return await plan_coverage_link_repository.get_coverages_by_plan(session, plan_id)

async def create_coverage_link(session: AsyncSession, payload: PlanCoverageLinkCreate, plan_id: UUID) -> PlanCoverageLink:
    link = PlanCoverageLink(**payload.dict(), plan_id=plan_id)
    return await plan_coverage_link_repository.create_coverage_link(session, link)
