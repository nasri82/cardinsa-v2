# app/modules/plans/services/plan_territory_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.modules.plans.models.plan_territory_model import PlanTerritory
from app.modules.plans.schemas.plan_territory_schema import PlanTerritoryCreate
from app.modules.plans.repositories import plan_territory_repository

async def list_territories_by_plan(session: AsyncSession, plan_id: UUID) -> list[PlanTerritory]:
    return await plan_territory_repository.get_territories_by_plan(session, plan_id)

async def create_territory(session: AsyncSession, payload: PlanTerritoryCreate, plan_id: UUID) -> PlanTerritory:
    territory = PlanTerritory(**payload.dict(), plan_id=plan_id)
    return await plan_territory_repository.create_territory(session, territory)
