from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.modules.pricing.calculations.schemas.premium_calculation_schema import (
    PremiumCalculationCreate,
    PremiumCalculationUpdate,
)
from app.modules.pricing.calculations.repositories import premium_calculation_repository as repo


def perform_premium_calculation(db: Session, data: PremiumCalculationCreate):
    # Optional: Add risk logic, AI model, or dynamic formula parser here
    return repo.create_premium_calculation(db, data)


def approve_premium(db: Session, calculation_id: UUID, approver_id: UUID):
    obj = repo.get_premium_calculation(db, calculation_id)
    if not obj:
        return None
    updates = PremiumCalculationUpdate(
        approval_status="approved",
        approved_by=approver_id,
        approved_at=datetime.utcnow(),
    )
    return repo.update_premium_calculation(db, obj, updates)
