from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.repositories import pricing_deductible_repository as repo
from app.modules.pricing.modifiers.schemas.pricing_deductible_schema import (
    PricingDeductibleCreate,
    PricingDeductibleUpdate,
)
from app.modules.pricing.modifiers.models.pricing_deductible_model import PricingDeductible

def get_all(db: Session) -> List[PricingDeductible]:
    return repo.get_all(db)

def get_by_id(db: Session, id: UUID) -> Optional[PricingDeductible]:
    return repo.get_by_id(db, id)

def create(db: Session, data: PricingDeductibleCreate) -> PricingDeductible:
    return repo.create(db, data)

def update(db: Session, id: UUID, data: PricingDeductibleUpdate) -> Optional[PricingDeductible]:
    db_obj = repo.get_by_id(db, id)
    if not db_obj:
        return None
    return repo.update(db, db_obj, data)

def delete(db: Session, id: UUID) -> bool:
    return repo.delete(db, id)
