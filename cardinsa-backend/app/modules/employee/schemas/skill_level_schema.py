from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillLevelCreate(BaseModel):
    name: str
    description: str


class SkillLevelUpdate(SkillLevelCreate):
    pass


class SkillLevelOut(SkillLevelCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime