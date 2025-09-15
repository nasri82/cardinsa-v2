# app/modules/benefits/routes/plan_benefit_schedule_route.py

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_permission_scoped
from app.modules.benefits.schemas.plan_benefit_schedule_schema import (
    PlanBenefitScheduleCreate,
    PlanBenefitScheduleUpdate,
    PlanBenefitScheduleOut,
)
from app.modules.benefits.services import plan_benefit_schedule_service

router = APIRouter(prefix="/plans/{plan_id}/benefit-schedules", tags=["Plan Benefit Schedules"])

@router.get("/", response_model=list[PlanBenefitScheduleOut])
async def list_schedules(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "view"))
):
    return await plan_benefit_schedule_service.list_schedules_by_plan(session, plan_id)

@router.get("/{schedule_id}", response_model=PlanBenefitScheduleOut)
async def get_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "view"))
):
    schedule = await plan_benefit_schedule_service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Benefit schedule not found")
    return schedule

@router.post("/", response_model=PlanBenefitScheduleOut)
async def create_schedule(
    plan_id: UUID,
    payload: PlanBenefitScheduleCreate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "create"))
):
    return await plan_benefit_schedule_service.create_schedule(session, payload, plan_id)

@router.put("/{schedule_id}", response_model=PlanBenefitScheduleOut)
async def update_schedule(
    schedule_id: UUID,
    payload: PlanBenefitScheduleUpdate,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "update"))
):
    schedule = await plan_benefit_schedule_service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Benefit schedule not found")
    return await plan_benefit_schedule_service.update_schedule(session, schedule, payload)

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission_scoped("benefits", "delete"))
):
    schedule = await plan_benefit_schedule_service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Benefit schedule not found")
    await plan_benefit_schedule_service.delete_schedule(session, schedule)
    return {"detail": "Deleted"}
