from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MotorExclusionCategoryBase(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    description: Optional[str] = None


class MotorExclusionCategoryCreate(MotorExclusionCategoryBase):
    pass


class MotorExclusionCategoryUpdate(MotorExclusionCategoryBase):
    pass


class MotorExclusionCategoryRead(MotorExclusionCategoryBase):
    id: UUID

    class Config:
        orm_mode = True
