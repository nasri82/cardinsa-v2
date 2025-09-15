# app/modules/plans/schemas/plan_exclusion_schema.py

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date

class PlanExclusionBase(BaseModel):
    exclusion_text: str
    exclusion_text_ar: Optional[str]
    exclusion_category: Optional[str]
    exclusion_severity: Optional[str]
    effective_date: Optional[date]
    expiry_date: Optional[date]
    geographic_scope: Optional[List[str]]
    regulatory_basis: Optional[str]
    exception_conditions: Optional[dict]

class PlanExclusionCreate(PlanExclusionBase):
    pass

class PlanExclusionUpdate(PlanExclusionBase):
    pass

class PlanExclusionOut(PlanExclusionBase):
    id: UUID

    class Config:
        orm_mode = True
