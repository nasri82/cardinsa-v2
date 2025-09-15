from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.models.pricing_copayment_model import PricingCopayment
from app.modules.pricing.modifiers.schemas.pricing_copayment_schema import (
    PricingCopaymentCreate,
    PricingCopaymentUpdate,
)

def get_all(db: Session) -> List[PricingCopayment]:
    return db.query(PricingCopayment).all()

def get_by_id(db: Session, id: UUID) -> Optional[PricingCopayment]:
    return db.query(PricingCopayment).filter(PricingCopayment.id == id).first()

def create(db: Session, data: PricingCopaymentCreate) -> PricingCopayment:
    obj = PricingCopayment(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: PricingCopayment, data: PricingCopaymentUpdate) -> PricingCopayment:
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
