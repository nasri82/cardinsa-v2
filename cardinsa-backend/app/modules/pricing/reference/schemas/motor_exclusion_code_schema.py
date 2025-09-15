from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MotorExclusionCodeBase(BaseModel):
    code: str
    reason_en: str
    reason_ar: Optional[str] = None
    category_id: Optional[UUID] = None


class MotorExclusionCodeCreate(MotorExclusionCodeBase):
    pass


class MotorExclusionCodeUpdate(MotorExclusionCodeBase):
    pass


class MotorExclusionCodeRead(MotorExclusionCodeBase):
    id: UUID

    class Config:
        orm_mode = True
