# app/modules/plans/schemas/plan_territory_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class PlanTerritoryBase(BaseModel):
    territory_type: str
    territory_code: Optional[str]
    territory_name: Optional[str]
    is_active: Optional[bool] = True
    effective_date: Optional[date]
    expiry_date: Optional[date]
    rate_adjustments: Optional[dict]
    regulatory_requirements: Optional[dict]

class PlanTerritoryCreate(PlanTerritoryBase):
    pass

class PlanTerritoryUpdate(PlanTerritoryBase):
    pass

class PlanTerritoryOut(PlanTerritoryBase):
    id: UUID
    plan_id: UUID

    class Config:
        orm_mode = True
