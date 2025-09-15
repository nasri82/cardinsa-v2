from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class CPTCodeBase(BaseModel):
    code: str = Field(..., max_length=20)
    description_en: str
    description_ar: Optional[str] = None
    category: Optional[str] = None


class CPTCodeCreate(CPTCodeBase):
    pass


class CPTCodeUpdate(CPTCodeBase):
    pass


class CPTCodeRead(CPTCodeBase):
    id: UUID

    class Config:
        orm_mode = True
