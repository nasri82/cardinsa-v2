# app/modules/plans/repositories/plan_exclusion_link_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_exclusion_link_model import PlanExclusionLink
from uuid import UUID

async def get_exclusions_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanExclusionLink]:
    result = await session.execute(select(PlanExclusionLink).where(PlanExclusionLink.plan_id == plan_id))
    return result.scalars().all()

async def create_exclusion_link(session: AsyncSession, link: PlanExclusionLink) -> PlanExclusionLink:
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link

async def delete_exclusion_link(session: AsyncSession, link: PlanExclusionLink) -> None:
    await session.delete(link)
    await session.commit()
