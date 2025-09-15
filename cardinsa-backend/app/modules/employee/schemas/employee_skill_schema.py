from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class EmployeeSkillCreate(BaseModel):
    employee_id: UUID
    skill_id: UUID
    proficiency_level: str
    score: float
    assessed_at: datetime
    valid_until: datetime


class EmployeeSkillUpdate(EmployeeSkillCreate):
    pass


class EmployeeSkillOut(EmployeeSkillCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime