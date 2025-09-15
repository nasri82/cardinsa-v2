from pydantic import BaseModel, Field
from pydantic import ConfigDict
from uuid import UUID
from datetime import datetime

class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=60)
    description: str | None = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=60)
    description: str | None = None
    is_active: bool | None = None

class CompanyOut(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
