# app/modules/plans/repositories/plan_territory_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.plans.models.plan_territory_model import PlanTerritory
from uuid import UUID

async def get_territories_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanTerritory]:
    result = await session.execute(select(PlanTerritory).where(PlanTerritory.plan_id == plan_id))
    return result.scalars().all()

async def create_territory(session: AsyncSession, territory: PlanTerritory) -> PlanTerritory:
    session.add(territory)
    await session.commit()
    await session.refresh(territory)
    return territory

async def delete_territory(session: AsyncSession, territory: PlanTerritory) -> None:
    await session.delete(territory)
    await session.commit()
