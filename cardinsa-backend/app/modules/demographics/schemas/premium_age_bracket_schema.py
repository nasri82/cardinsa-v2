from pydantic import BaseModel
from uuid import UUID
from datetime import date

class PremiumAgeBracketBase(BaseModel):
    plan_id: UUID
    age_bracket_id: UUID
    multiplier: float
    valid_from: date | None = None
    valid_to: date | None = None

class PremiumAgeBracketCreate(PremiumAgeBracketBase):
    pass

class PremiumAgeBracketUpdate(PremiumAgeBracketBase):
    pass

class PremiumAgeBracketOut(PremiumAgeBracketBase):
    id: UUID

    class Config:
        orm_mode = True
