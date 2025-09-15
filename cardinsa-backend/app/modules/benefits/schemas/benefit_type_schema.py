from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class BenefitTypeBase(BaseModel):
    type_code: str
    type_name: str
    type_name_ar: Optional[str]
    type_name_fr: Optional[str]
    calculation_method: Optional[str]
    unit_of_measure: Optional[str]
    is_active: Optional[bool] = True


class BenefitTypeCreate(BenefitTypeBase):
    pass


class BenefitTypeUpdate(BenefitTypeBase):
    pass


class BenefitTypeOut(BenefitTypeBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


    class Config:
        orm_mode = True