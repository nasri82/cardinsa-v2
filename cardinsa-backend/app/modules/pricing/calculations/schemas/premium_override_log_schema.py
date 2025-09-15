from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PremiumOverrideLogBase(BaseModel):
    calculation_id: UUID
    original_value: float
    overridden_value: float
    reason: Optional[str] = None
    overridden_by: UUID


class PremiumOverrideLogCreate(PremiumOverrideLogBase):
    pass


class PremiumOverrideLogOut(PremiumOverrideLogBase):
    id: UUID
    overridden_at: datetime

    class Config:
        orm_mode = True
