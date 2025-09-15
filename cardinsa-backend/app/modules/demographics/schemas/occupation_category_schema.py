from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class OccupationCategoryBase(BaseModel):
    code: str
    name: str
    risk_level: Optional[str] = None

class OccupationCategoryCreate(OccupationCategoryBase):
    pass

class OccupationCategoryUpdate(OccupationCategoryBase):
    pass

class OccupationCategoryOut(OccupationCategoryBase):
    id: UUID

    class Config:
        orm_mode = True
