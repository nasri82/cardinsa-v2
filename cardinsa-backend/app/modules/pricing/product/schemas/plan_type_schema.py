from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class PlanTypeBase(BaseModel):
    code: str
    name_en: str
    name_ar: Optional[str]
    description: Optional[str]
    is_active: Optional[bool] = True


class PlanTypeCreate(PlanTypeBase):
    pass


class PlanTypeUpdate(PlanTypeBase):
    pass


class PlanTypeRead(PlanTypeBase):
    id: UUID

    class Config:
        orm_mode = True
