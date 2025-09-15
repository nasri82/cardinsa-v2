from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.modules.pricing.modifiers.services import pricing_discount_service as service
from app.modules.pricing.modifiers.schemas.pricing_discount_schema import (
    PricingDiscount,
    PricingDiscountCreate,
    PricingDiscountUpdate,
)

router = APIRouter(prefix="/discounts", tags=["Discounts"])

@router.get("/", response_model=List[PricingDiscount])
def list_all(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{id}", response_model=PricingDiscount)
def get_one(id: UUID, db: Session = Depends(get_db)):
    obj = service.get_by_id(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Discount not found")
    return obj

@router.post("/", response_model=PricingDiscount)
def create(data: PricingDiscountCreate, db: Session = Depends(get_db)):
    return service.create(db, data)

@router.put("/{id}", response_model=PricingDiscount)
def update(id: UUID, data: PricingDiscountUpdate, db: Session = Depends(get_db)):
    obj = service.update(db, id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Discount not found")
    return obj

@router.delete("/{id}")
def delete(id: UUID, db: Session = Depends(get_db)):
    success = service.delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Discount not found")
    return {"success": True}
