# app/modules/plans/routes/plan_route.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.plans.schemas.plan_schema import PlanCreate, PlanUpdate, PlanOut
from app.modules.plans.services import plan_service

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.get("/", response_model=list[PlanOut])
async def list_plans(
    skip: int = 0, limit: int = 100,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    return await plan_service.list_plans(session, skip, limit)

@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "view"))
):
    plan = await plan_service.get_plan(session, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.post("/", response_model=PlanOut)
async def create_plan(
    payload: PlanCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "create"))
):
    return await plan_service.create_plan(session, payload)

@router.put("/{plan_id}", response_model=PlanOut)
async def update_plan(
    plan_id: UUID,
    payload: PlanUpdate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "update"))
):
    plan = await plan_service.get_plan(session, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return await plan_service.update_plan(session, plan, payload)

@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("plans", "delete"))
):
    plan = await plan_service.get_plan(session, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await plan_service.delete_plan(session, plan)
    return {"detail": "Deleted"}
