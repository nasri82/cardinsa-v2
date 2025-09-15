# app/modules/plans/repositories/plan_coverage_link_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_coverage_link_model import PlanCoverageLink
from uuid import UUID

async def get_coverages_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanCoverageLink]:
    result = await session.execute(select(PlanCoverageLink).where(PlanCoverageLink.plan_id == plan_id))
    return result.scalars().all()

async def create_coverage_link(session: AsyncSession, link: PlanCoverageLink) -> PlanCoverageLink:
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link

async def delete_coverage_link(session: AsyncSession, link: PlanCoverageLink) -> None:
    await session.delete(link)
    await session.commit()
