from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ---------- Inbound ----------

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    # If your User model is tenant-scoped, keep company_id; otherwise remove it.
    company_id: Optional[UUID] = None
    is_active: bool = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class ChangePasswordIn(BaseModel):
    new_password: str = Field(min_length=8)

# ---------- Outbound ----------

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    company_id: Optional[UUID] = None
    roles: List[str] = []  # role slugs or names
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
