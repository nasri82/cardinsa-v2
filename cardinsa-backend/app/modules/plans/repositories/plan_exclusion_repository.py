# app/modules/plans/repositories/plan_exclusion_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_exclusion_model import PlanExclusion
from uuid import UUID

async def get_exclusion_by_id(session: AsyncSession, exclusion_id: UUID) -> PlanExclusion | None:
    result = await session.execute(select(PlanExclusion).where(PlanExclusion.id == exclusion_id))
    return result.scalars().first()

async def create_exclusion(session: AsyncSession, exclusion: PlanExclusion) -> PlanExclusion:
    session.add(exclusion)
    await session.commit()
    await session.refresh(exclusion)
    return exclusion
