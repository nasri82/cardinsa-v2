# app/modules/pricing/modifiers/services/pricing_commission_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.repositories import pricing_commission_repository as repo
from app.modules.pricing.modifiers.schemas.pricing_commission_schema import (
    PricingCommissionCreate,
    PricingCommissionUpdate,
)
from app.modules.pricing.modifiers.models.pricing_commission_model import PricingCommission

def get_all(db: Session) -> List[PricingCommission]:
    return repo.get_all(db)

def get_by_id(db: Session, id: UUID) -> Optional[PricingCommission]:
    return repo.get_by_id(db, id)

def create(db: Session, data: PricingCommissionCreate) -> PricingCommission:
    return repo.create(db, data)

def update(db: Session, id: UUID, data: PricingCommissionUpdate) -> Optional[PricingCommission]:
    db_obj = repo.get_by_id(db, id)
    if not db_obj:
        return None
    return repo.update(db, db_obj, data)

def delete(db: Session, id: UUID) -> bool:
    return repo.delete(db, id)
