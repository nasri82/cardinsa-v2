from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SkillsDemandForecastCreate(BaseModel):
    skill: str
    demand_score: float
    growth_rate: float
    automation_threat: str


class SkillsDemandForecastUpdate(SkillsDemandForecastCreate):
    pass


class SkillsDemandForecastOut(SkillsDemandForecastCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime