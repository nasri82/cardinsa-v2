from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=80)
    description: Optional[str] = None
    is_active: bool = True

class RoleOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool
    class Config:
        from_attributes = True
