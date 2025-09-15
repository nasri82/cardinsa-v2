from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillsDevelopmentPlanCreate(BaseModel):
    employee_id: UUID
    target_skills: List[str]
    duration_months: int
    estimated_cost: float


class SkillsDevelopmentPlanUpdate(SkillsDevelopmentPlanCreate):
    pass


class SkillsDevelopmentPlanOut(SkillsDevelopmentPlanCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime