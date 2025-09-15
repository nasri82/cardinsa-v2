from sqlalchemy.orm import Session
from app.modules.pricing.calculations.models.premium_override_log_model import PremiumOverrideLog
from app.modules.pricing.calculations.schemas.premium_override_log_schema import PremiumOverrideLogCreate


def create_override_log(db: Session, data: PremiumOverrideLogCreate) -> PremiumOverrideLog:
    db_obj = PremiumOverrideLog(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def list_override_logs_by_calculation(db: Session, calculation_id):
    return db.query(PremiumOverrideLog).filter(PremiumOverrideLog.calculation_id == calculation_id).all()
