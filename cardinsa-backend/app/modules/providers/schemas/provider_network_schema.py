from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProviderNetworkBase(BaseModel):
    name: str
    tier: Optional[str] = None
    description: Optional[str] = None

class ProviderNetworkCreate(ProviderNetworkBase):
    pass

class ProviderNetworkUpdate(ProviderNetworkBase):
    pass

class ProviderNetworkOut(ProviderNetworkBase):
    id: UUID

    class Config:
        orm_mode = True
