from sqlalchemy.orm import Session
from app.modules.pricing.calculations.schemas.premium_override_log_schema import PremiumOverrideLogCreate
from app.modules.pricing.calculations.repositories import premium_override_log_repository as repo


def log_override(db: Session, data: PremiumOverrideLogCreate):
    # Optional: Add audit validation, logging, or notify supervisor
    return repo.create_override_log(db, data)
