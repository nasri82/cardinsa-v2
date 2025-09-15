from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MedicalExclusionCodeBase(BaseModel):
    code: str
    reason_en: str
    reason_ar: Optional[str] = None
    category_id: Optional[UUID] = None


class MedicalExclusionCodeCreate(MedicalExclusionCodeBase):
    pass


class MedicalExclusionCodeUpdate(MedicalExclusionCodeBase):
    pass


class MedicalExclusionCodeRead(MedicalExclusionCodeBase):
    id: UUID

    class Config:
        orm_mode = True
