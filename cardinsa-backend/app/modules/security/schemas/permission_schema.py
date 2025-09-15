from pydantic import BaseModel

class PermissionBase(BaseModel):
    pass

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: str | None = None
