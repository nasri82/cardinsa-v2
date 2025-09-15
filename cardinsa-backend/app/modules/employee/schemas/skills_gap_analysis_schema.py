from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillsGapAnalysisCreate(BaseModel):
    department_id: UUID
    current_skills: List[str]
    future_skills: List[str]
    gap_severity: str


class SkillsGapAnalysisUpdate(SkillsGapAnalysisCreate):
    pass


class SkillsGapAnalysisOut(SkillsGapAnalysisCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime