# app/modules/pricing/modifiers/services/pricing_discount_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.repositories import pricing_discount_repository as repo
from app.modules.pricing.modifiers.schemas.pricing_discount_schema import (
    PricingDiscountCreate,
    PricingDiscountUpdate,
)
from app.modules.pricing.modifiers.models.pricing_discount_model import PricingDiscount

def get_all(db: Session) -> List[PricingDiscount]:
    return repo.get_all(db)

def get_by_id(db: Session, id: UUID) -> Optional[PricingDiscount]:
    return repo.get_by_id(db, id)

def create(db: Session, data: PricingDiscountCreate) -> PricingDiscount:
    return repo.create(db, data)

def update(db: Session, id: UUID, data: PricingDiscountUpdate) -> Optional[PricingDiscount]:
    db_obj = repo.get_by_id(db, id)
    if not db_obj:
        return None
    return repo.update(db, db_obj, data)

def delete(db: Session, id: UUID) -> bool:
    return repo.delete(db, id)