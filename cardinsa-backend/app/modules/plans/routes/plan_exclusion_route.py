# app/modules/plans/routes/plan_exclusion_route.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_exclusion_schema import PlanExclusionCreate, PlanExclusionOut
from app.modules.plans.services import plan_exclusion_service

router = APIRouter(prefix="/plan-exclusions", tags=["Plan Exclusions"])

@router.post("/", response_model=PlanExclusionOut)
async def create_exclusion(
    payload: PlanExclusionCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_exclusion_service.create_exclusion(session, payload)
