# app/modules/pricing/profiles/schemas/demographic_schema.py
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from enum import Enum

class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F" 
    UNSPECIFIED = "U"

class DemographicProfileSchema(BaseModel):
    age: int
    gender: Gender
    territory: str
    occupation: Optional[str] = None
    risk_factors: List[str] = []

class DemographicPricingRequest(BaseModel):
    base_premium: Decimal
    demographic_profile: DemographicProfileSchema
    benefit_type: Optional[str] = None
    include_actuarial: bool = True