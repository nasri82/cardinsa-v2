# app/modules/plans/schemas/plan_schema.py

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import date
from .plan_coverage_link_schema import PlanCoverageLinkOut
from .plan_exclusion_link_schema import PlanExclusionLinkOut
from .plan_version_schema import PlanVersionOut
from .plan_territory_schema import PlanTerritoryOut
from .plan_eligibility_rule_schema import PlanEligibilityRuleOut

class PlanBase(BaseModel):
    name: str
    name_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    plan_type_id: Optional[UUID]
    company_id: Optional[UUID]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: Optional[bool] = True
    version: Optional[str]
    regulatory_approval_status: Optional[str]
    policy_terms_url: Optional[HttpUrl]
    commission_structure: Optional[str]
    target_market_segment: Optional[str]
    distribution_channels: Optional[str]
    underwriting_guidelines: Optional[str]

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class PlanOut(PlanBase):
    id: UUID
    coverages: Optional[List[PlanCoverageLinkOut]] = []
    exclusions: Optional[List[PlanExclusionLinkOut]] = []
    versions: Optional[List[PlanVersionOut]] = []
    territories: Optional[List[PlanTerritoryOut]] = []
    eligibility_rules: Optional[List[PlanEligibilityRuleOut]] = []

    class Config:
        orm_mode = True
