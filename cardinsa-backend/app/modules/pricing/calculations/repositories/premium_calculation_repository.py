from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.pricing.calculations.models.premium_calculation_model import PremiumCalculation
from app.modules.pricing.calculations.schemas.premium_calculation_schema import PremiumCalculationCreate, PremiumCalculationUpdate


def get_premium_calculation(db: Session, calculation_id: UUID) -> PremiumCalculation:
    return db.query(PremiumCalculation).filter(PremiumCalculation.id == calculation_id).first()


def create_premium_calculation(db: Session, data: PremiumCalculationCreate) -> PremiumCalculation:
    db_obj = PremiumCalculation(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_premium_calculation(db: Session, obj: PremiumCalculation, data: PremiumCalculationUpdate) -> PremiumCalculation:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def list_premium_calculations_by_quotation(db: Session, quotation_id: UUID):
    return db.query(PremiumCalculation).filter(PremiumCalculation.quotation_id == quotation_id).all()
