# app/modules/plans/routes/plan_version_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_version_schema import PlanVersionCreate, PlanVersionOut
from app.modules.plans.services import plan_version_service

router = APIRouter(prefix="/plans/{plan_id}/versions", tags=["Plan Versions"])

@router.get("/", response_model=list[PlanVersionOut])
async def list_versions(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_version_service.list_versions_by_plan(session, plan_id)

@router.post("/", response_model=PlanVersionOut)
async def create_version(
    plan_id: UUID,
    payload: PlanVersionCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_version_service.create_version(session, payload, plan_id)
