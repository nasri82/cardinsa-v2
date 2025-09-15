

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CoverageOptionBase(BaseModel):
    coverage_id: UUID
    name: str
    name_ar: Optional[str]
    name_fr: Optional[str]
    value: Optional[str]
    display_order: Optional[int]
    is_default: Optional[bool] = False
    is_mandatory: Optional[bool] = False
    option_group_code: Optional[str]
    eligibility_criteria: Optional[str]
    geographic_restrictions: Optional[str]
    exclusion_tags: Optional[str]


class CoverageOptionCreate(CoverageOptionBase):
    pass


class CoverageOptionUpdate(CoverageOptionBase):
    pass


class CoverageOptionOut(CoverageOptionBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


    class Config:
        orm_mode = True