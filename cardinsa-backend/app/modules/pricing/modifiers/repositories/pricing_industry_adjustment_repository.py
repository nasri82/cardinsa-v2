from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.models.pricing_industry_adjustment_model import PricingIndustryAdjustment
from app.modules.pricing.modifiers.schemas.pricing_industry_adjustment_schema import (
    PricingIndustryAdjustmentCreate,
    PricingIndustryAdjustmentUpdate,
)

def get_all(db: Session) -> List[PricingIndustryAdjustment]:
    return db.query(PricingIndustryAdjustment).all()

def get_by_id(db: Session, id: UUID) -> Optional[PricingIndustryAdjustment]:
    return db.query(PricingIndustryAdjustment).filter(PricingIndustryAdjustment.id == id).first()

def create(db: Session, data: PricingIndustryAdjustmentCreate) -> PricingIndustryAdjustment:
    obj = PricingIndustryAdjustment(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: PricingIndustryAdjustment, data: PricingIndustryAdjustmentUpdate) -> PricingIndustryAdjustment:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, id: UUID) -> bool:
    obj = get_by_id(db, id)
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False
