# app/modules/plans/schemas/plan_exclusion_link_schema.py

from pydantic import BaseModel
from uuid import UUID

class PlanExclusionLinkBase(BaseModel):
    exclusion_id: UUID

class PlanExclusionLinkCreate(PlanExclusionLinkBase):
    pass

class PlanExclusionLinkUpdate(PlanExclusionLinkBase):
    pass

class PlanExclusionLinkOut(PlanExclusionLinkBase):
    id: UUID
    plan_id: UUID

    class Config:
        orm_mode = True
