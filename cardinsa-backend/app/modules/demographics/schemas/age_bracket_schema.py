from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class InsuranceTypeEnum(str, Enum):
    medical = "medical"
    motor = "motor"
    life = "life"
    travel = "travel"

class AgeBracketBase(BaseModel):
    min_age: int
    max_age: int
    gender: Optional[GenderEnum]
    insurance_type: Optional[InsuranceTypeEnum]
    effective_date: Optional[date]

class AgeBracketCreate(AgeBracketBase):
    pass

class AgeBracketUpdate(AgeBracketBase):
    pass

class AgeBracketOut(AgeBracketBase):
    id: UUID

    class Config:
        orm_mode = True
