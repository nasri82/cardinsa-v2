# app/modules/plans/services/plan_exclusion_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.plans.models.plan_exclusion_model import PlanExclusion
from app.modules.plans.schemas.plan_exclusion_schema import PlanExclusionCreate
from app.modules.plans.repositories import plan_exclusion_repository

async def create_exclusion(session: AsyncSession, payload: PlanExclusionCreate) -> PlanExclusion:
    exclusion = PlanExclusion(**payload.dict())
    return await plan_exclusion_repository.create_exclusion(session, exclusion)
