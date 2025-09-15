from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.modules.pricing.modifiers.services import pricing_industry_adjustment_service as service
from app.modules.pricing.modifiers.schemas.pricing_industry_adjustment_schema import (
    PricingIndustryAdjustment,
    PricingIndustryAdjustmentCreate,
    PricingIndustryAdjustmentUpdate,
)

router = APIRouter(prefix="/industry-adjustments", tags=["Industry Adjustments"])

@router.get("/", response_model=List[PricingIndustryAdjustment])
def list_all(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{id}", response_model=PricingIndustryAdjustment)
def get_one(id: UUID, db: Session = Depends(get_db)):
    obj = service.get_by_id(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Industry adjustment not found")
    return obj

@router.post("/", response_model=PricingIndustryAdjustment)
def create(data: PricingIndustryAdjustmentCreate, db: Session = Depends(get_db)):
    return service.create(db, data)

@router.put("/{id}", response_model=PricingIndustryAdjustment)
def update(id: UUID, data: PricingIndustryAdjustmentUpdate, db: Session = Depends(get_db)):
    obj = service.update(db, id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Industry adjustment not found")
    return obj

@router.delete("/{id}")
def delete(id: UUID, db: Session = Depends(get_db)):
    success = service.delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Industry adjustment not found")
    return {"success": True}
