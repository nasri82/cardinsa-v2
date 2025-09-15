from pydantic import BaseModel
from uuid import UUID

class ProviderTypeBase(BaseModel):
    name: str
    category: str

class ProviderTypeCreate(ProviderTypeBase):
    pass

class ProviderTypeUpdate(ProviderTypeBase):
    pass

class ProviderTypeOut(ProviderTypeBase):
    id: UUID

    class Config:
        orm_mode = True
