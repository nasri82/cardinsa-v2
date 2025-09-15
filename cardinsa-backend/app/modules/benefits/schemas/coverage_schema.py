from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class CoverageBase(BaseModel):
    name: str
    name_ar: Optional[str]
    name_fr: Optional[str]
    description: Optional[str]
    coverage_code: Optional[str]
    category_id: Optional[UUID]
    parent_coverage_id: Optional[UUID]
    benefit_type_id: Optional[UUID]
    limit_amount: Optional[float]
    co_payment: Optional[float]
    deductible: Optional[float]
    frequency_limit: Optional[int]
    max_visits: Optional[int]
    unit_type: Optional[str]
    waiting_period_days: Optional[int]
    effective_date: Optional[date]
    expiry_date: Optional[date]
    authorization_required: Optional[bool] = False
    is_active: Optional[bool] = True
    regulatory_code: Optional[str]


class CoverageCreate(CoverageBase):
    pass


class CoverageUpdate(CoverageBase):
    pass


class CoverageOut(CoverageBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


    class Config:
        orm_mode = True