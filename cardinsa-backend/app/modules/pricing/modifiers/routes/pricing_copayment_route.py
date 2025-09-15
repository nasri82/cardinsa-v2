from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.modules.pricing.modifiers.services import pricing_copayment_service as service
from app.modules.pricing.modifiers.schemas.pricing_copayment_schema import (
    PricingCopayment,
    PricingCopaymentCreate,
    PricingCopaymentUpdate,
)

router = APIRouter(prefix="/copayments", tags=["Copayments"])

@router.get("/", response_model=List[PricingCopayment])
def list_all(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{id}", response_model=PricingCopayment)
def get_one(id: UUID, db: Session = Depends(get_db)):
    obj = service.get_by_id(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Copayment not found")
    return obj

@router.post("/", response_model=PricingCopayment)
def create(data: PricingCopaymentCreate, db: Session = Depends(get_db)):
    return service.create(db, data)

@router.put("/{id}", response_model=PricingCopayment)
def update(id: UUID, data: PricingCopaymentUpdate, db: Session = Depends(get_db)):
    obj = service.update(db, id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Copayment not found")
    return obj

@router.delete("/{id}")
def delete(id: UUID, db: Session = Depends(get_db)):
    success = service.delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Copayment not found")
    return {"success": True}
