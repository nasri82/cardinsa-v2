from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class MedicalExclusionCategoryBase(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    description: Optional[str] = None


class MedicalExclusionCategoryCreate(MedicalExclusionCategoryBase):
    pass


class MedicalExclusionCategoryUpdate(MedicalExclusionCategoryBase):
    pass


class MedicalExclusionCategoryRead(MedicalExclusionCategoryBase):
    id: UUID

    class Config:
        orm_mode = True
