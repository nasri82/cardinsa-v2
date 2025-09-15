from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ActuarialTableBase(BaseModel):
    gender: str
    min_age: int
    max_age: int
    risk_factor: float
    region: Optional[str]
    year: Optional[int]


class ActuarialTableCreate(ActuarialTableBase):
    pass


class ActuarialTableUpdate(ActuarialTableBase):
    pass


class ActuarialTableRead(ActuarialTableBase):
    id: UUID

    class Config:
        orm_mode = True
