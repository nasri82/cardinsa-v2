# app/modules/benefits/schemas/benefit_translation_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BenefitTranslationBase(BaseModel):
    language_code: str
    name: str
    description: Optional[str]

class BenefitTranslationCreate(BenefitTranslationBase):
    pass

class BenefitTranslationUpdate(BenefitTranslationBase):
    pass

class BenefitTranslationOut(BenefitTranslationBase):
    id: UUID
    schedule_id: UUID

    class Config:
        orm_mode = True
