# app/modules/plans/routes/plan_coverage_link_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_coverage_link_schema import PlanCoverageLinkCreate, PlanCoverageLinkOut
from app.modules.plans.services import plan_coverage_link_service

router = APIRouter(prefix="/plans/{plan_id}/coverages", tags=["Plan Coverages"])

@router.get("/", response_model=list[PlanCoverageLinkOut])
async def list_coverages(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_coverage_link_service.list_coverages_by_plan(session, plan_id)

@router.post("/", response_model=PlanCoverageLinkOut)
async def add_coverage(
    plan_id: UUID,
    payload: PlanCoverageLinkCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_coverage_link_service.create_coverage_link(session, payload, plan_id)
