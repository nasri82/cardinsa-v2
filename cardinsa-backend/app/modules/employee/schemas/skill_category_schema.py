from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillCategoryCreate(BaseModel):
    name: str
    description: str


class SkillCategoryUpdate(SkillCategoryCreate):
    pass


class SkillCategoryOut(SkillCategoryCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime