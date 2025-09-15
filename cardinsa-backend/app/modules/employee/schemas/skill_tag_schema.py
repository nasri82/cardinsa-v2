from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillTagCreate(BaseModel):
    name: str


class SkillTagUpdate(SkillTagCreate):
    pass


class SkillTagOut(SkillTagCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime