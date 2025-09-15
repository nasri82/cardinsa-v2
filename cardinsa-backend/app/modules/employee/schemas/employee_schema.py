from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class EmployeeCreate(BaseModel):
    full_name: str
    email: str
    phone_number: str
    job_title: str
    department_id: UUID
    company_id: UUID
    unit_id: UUID
    is_active: bool


class EmployeeUpdate(EmployeeCreate):
    pass


class EmployeeOut(EmployeeCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime