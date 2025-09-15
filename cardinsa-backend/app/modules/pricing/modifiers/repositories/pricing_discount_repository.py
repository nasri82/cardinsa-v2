from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.models.pricing_discount_model import PricingDiscount
from app.modules.pricing.modifiers.schemas.pricing_discount_schema import (
    PricingDiscountCreate,
    PricingDiscountUpdate,
)

def get_all(db: Session) -> List[PricingDiscount]:
    return db.query(PricingDiscount).all()

def get_by_id(db: Session, id: UUID) -> Optional[PricingDiscount]:
    return db.query(PricingDiscount).filter(PricingDiscount.id == id).first()

def create(db: Session, data: PricingDiscountCreate) -> PricingDiscount:
    obj = PricingDiscount(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: PricingDiscount, data: PricingDiscountUpdate) -> PricingDiscount:
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
