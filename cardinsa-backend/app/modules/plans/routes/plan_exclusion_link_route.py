# app/modules/plans/routes/plan_exclusion_link_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_exclusion_link_schema import PlanExclusionLinkCreate, PlanExclusionLinkOut
from app.modules.plans.services import plan_exclusion_link_service

router = APIRouter(prefix="/plans/{plan_id}/exclusions", tags=["Plan Exclusions"])

@router.get("/", response_model=list[PlanExclusionLinkOut])
async def list_exclusions(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_exclusion_link_service.list_exclusions_by_plan(session, plan_id)

@router.post("/", response_model=PlanExclusionLinkOut)
async def add_exclusion_link(
    plan_id: UUID,
    payload: PlanExclusionLinkCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_exclusion_link_service.create_exclusion_link(session, payload, plan_id)
