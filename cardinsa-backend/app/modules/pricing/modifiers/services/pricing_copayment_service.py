# app/modules/pricing/modifiers/services/pricing_copayment_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.repositories import pricing_copayment_repository as repo
from app.modules.pricing.modifiers.schemas.pricing_copayment_schema import (
    PricingCopaymentCreate,
    PricingCopaymentUpdate,
)
from app.modules.pricing.modifiers.models.pricing_copayment_model import PricingCopayment

def get_all(db: Session) -> List[PricingCopayment]:
    return repo.get_all(db)

def get_by_id(db: Session, id: UUID) -> Optional[PricingCopayment]:
    return repo.get_by_id(db, id)

def create(db: Session, data: PricingCopaymentCreate) -> PricingCopayment:
    return repo.create(db, data)

def update(db: Session, id: UUID, data: PricingCopaymentUpdate) -> Optional[PricingCopayment]:
    db_obj = repo.get_by_id(db, id)
    if not db_obj:
        return None
    return repo.update(db, db_obj, data)

def delete(db: Session, id: UUID) -> bool:
    return repo.delete(db, id)