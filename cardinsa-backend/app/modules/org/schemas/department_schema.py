from pydantic import BaseModel, Field
from pydantic import ConfigDict
from uuid import UUID
from datetime import datetime

class DepartmentBase(BaseModel):
    company_id: UUID
    name: str = Field(min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=60)
    description: str | None = None
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=60)
    description: str | None = None
    is_active: bool | None = None

class DepartmentOut(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
