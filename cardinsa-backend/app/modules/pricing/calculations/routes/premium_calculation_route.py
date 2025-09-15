from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.dependencies import get_db, get_current_user, require_permission_scoped
from app.modules.pricing.calculations.schemas.premium_calculation_schema import (
    PremiumCalculationCreate,
    PremiumCalculationOut,
    PremiumOverrideCreate,
    CalculationBreakdownOut,
    CalculationPerformanceMetrics,
)
from app.modules.pricing.calculations.services import premium_calculation_service as service

router = APIRouter(
    prefix="/premium-calculations",
    tags=["Premium Calculations"]
)


@router.post("/", response_model=PremiumCalculationOut)
def calculate_premium(
    data: PremiumCalculationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="create")
    return service.perform_premium_calculation(db, data)


@router.put("/{calculation_id}/approve", response_model=PremiumCalculationOut)
def approve_premium(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="approve")
    result = service.approve_premium(db, calculation_id, approver_id=user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return result

# Add to premium_calculation_route.py
@router.get("/{calculation_id}", response_model=PremiumCalculationOut)
def get_calculation(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="read")
    result = service.get_calculation(db, calculation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return result

@router.get("/", response_model=List[PremiumCalculationOut])
def list_calculations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="read")
    return service.list_calculations(db, skip=skip, limit=limit)

@router.put("/{calculation_id}/override", response_model=PremiumCalculationOut)
def override_premium(
    calculation_id: UUID,
    override_data: PremiumOverrideCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="override")
    return service.override_premium(db, calculation_id, override_data, user.id)

@router.get("/{calculation_id}/breakdown", response_model=CalculationBreakdownOut)
def get_calculation_breakdown(
    calculation_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="read")
    return service.get_detailed_breakdown(db, calculation_id)