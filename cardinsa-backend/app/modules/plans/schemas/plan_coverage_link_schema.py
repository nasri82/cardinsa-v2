# app/modules/plans/schemas/plan_coverage_link_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class PlanCoverageLinkBase(BaseModel):
    coverage_id: UUID
    limit: Optional[float]
    deductible: Optional[float]
    copay: Optional[float]
    coinsurance: Optional[float]
    coverage_tier: Optional[str]
    network_restrictions: Optional[dict]
    prior_authorization_required: Optional[bool] = False
    annual_maximum: Optional[float]
    lifetime_maximum: Optional[float]
    waiting_period_days: Optional[int]
    effective_date: Optional[date]
    expiry_date: Optional[date]
    geographic_restrictions: Optional[dict]
    is_mandatory: Optional[bool] = False

class PlanCoverageLinkCreate(PlanCoverageLinkBase):
    pass

class PlanCoverageLinkUpdate(PlanCoverageLinkBase):
    pass

class PlanCoverageLinkOut(PlanCoverageLinkBase):
    id: UUID
    plan_id: UUID

    class Config:
        orm_mode = True
