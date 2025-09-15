from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class ICD10CodeBase(BaseModel):
    code: str = Field(..., max_length=20)
    description_en: str
    description_ar: Optional[str] = None
    chapter: Optional[str] = None


class ICD10CodeCreate(ICD10CodeBase):
    pass


class ICD10CodeUpdate(ICD10CodeBase):
    pass


class ICD10CodeRead(ICD10CodeBase):
    id: UUID

    class Config:
        orm_mode = True
