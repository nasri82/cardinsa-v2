from pydantic import BaseModel, Field, model_validator
from pydantic import ConfigDict
from uuid import UUID
from datetime import datetime

class ScopedRoleBase(BaseModel):
    # Either role_id OR role_name is required
    role_id: UUID | None = None
    role_name: str | None = Field(default=None, min_length=1, max_length=160)

    # Optional scope (all nullable = global)
    company_id: UUID | None = None
    department_id: UUID | None = None
    unit_id: UUID | None = None

    @model_validator(mode="after")
    def _one_role_identifier(self):
        if not self.role_id and not self.role_name:
            raise ValueError("Provide either role_id or role_name")
        return self

class AssignRoleIn(ScopedRoleBase):
    pass

class RevokeRoleIn(ScopedRoleBase):
    pass

class UserRoleOut(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    company_id: UUID | None
    department_id: UUID | None
    unit_id: UUID | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
