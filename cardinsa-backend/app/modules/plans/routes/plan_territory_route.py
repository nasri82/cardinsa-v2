# app/modules/plans/routes/plan_territory_route.py

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_territory_schema import PlanTerritoryCreate, PlanTerritoryOut
from app.modules.plans.services import plan_territory_service

router = APIRouter(prefix="/plans/{plan_id}/territories", tags=["Plan Territories"])

@router.get("/", response_model=list[PlanTerritoryOut])
async def list_territories(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_territory_service.list_territories_by_plan(session, plan_id)

@router.post("/", response_model=PlanTerritoryOut)
async def create_territory(
    plan_id: UUID,
    payload: PlanTerritoryCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_territory_service.create_territory(session, payload, plan_id)
