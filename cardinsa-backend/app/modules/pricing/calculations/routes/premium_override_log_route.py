from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_permission_scoped
from app.modules.pricing.calculations.schemas.premium_override_log_schema import (
    PremiumOverrideLogCreate,
    PremiumOverrideLogOut,
)
from app.modules.pricing.calculations.services import premium_override_log_service as service

router = APIRouter(
    prefix="/premium-override-logs",
    tags=["Premium Overrides"]
)


@router.post("/", response_model=PremiumOverrideLogOut)
def create_override_log(
    data: PremiumOverrideLogCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    require_permission_scoped(user, module="pricing", action="override")
    return service.log_override(db, data)
