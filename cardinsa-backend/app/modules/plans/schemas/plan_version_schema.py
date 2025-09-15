# app/modules/plans/schemas/plan_version_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class PlanVersionBase(BaseModel):
    version_number: str
    version_description: Optional[str]
    changes_from_previous: Optional[dict]
    effective_date: date
    expiry_date: Optional[date]
    created_by_reason: Optional[str]
    regulatory_approval_required: Optional[bool] = False
    approval_status: Optional[str]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    is_current_version: Optional[bool] = False

class PlanVersionCreate(PlanVersionBase):
    pass

class PlanVersionUpdate(PlanVersionBase):
    pass

class PlanVersionOut(PlanVersionBase):
    id: UUID
    plan_id: UUID

    class Config:
        orm_mode = True
