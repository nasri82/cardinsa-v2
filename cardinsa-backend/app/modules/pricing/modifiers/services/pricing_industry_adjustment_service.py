# app/modules/pricing/modifiers/services/pricing_industry_adjustment_service.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.repositories import pricing_industry_adjustment_repository as repo
from app.modules.pricing.modifiers.schemas.pricing_industry_adjustment_schema import (
    PricingIndustryAdjustmentCreate,
    PricingIndustryAdjustmentUpdate,
)
from app.modules.pricing.modifiers.models.pricing_industry_adjustment_model import PricingIndustryAdjustment

def get_all(db: Session) -> List[PricingIndustryAdjustment]:
    return repo.get_all(db)

def get_by_id(db: Session, id: UUID) -> Optional[PricingIndustryAdjustment]:
    return repo.get_by_id(db, id)

def create(db: Session, data: PricingIndustryAdjustmentCreate) -> PricingIndustryAdjustment:
    return repo.create(db, data)

def update(db: Session, id: UUID, data: PricingIndustryAdjustmentUpdate) -> Optional[PricingIndustryAdjustment]:
    db_obj = repo.get_by_id(db, id)
    if not db_obj:
        return None
    return repo.update(db, db_obj, data)

def delete(db: Session, id: UUID) -> bool:
    return repo.delete(db, id)