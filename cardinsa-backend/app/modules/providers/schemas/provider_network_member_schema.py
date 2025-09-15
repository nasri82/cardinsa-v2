from pydantic import BaseModel
from uuid import UUID

class ProviderNetworkMemberBase(BaseModel):
    provider_id: UUID
    provider_network_id: UUID

class ProviderNetworkMemberCreate(ProviderNetworkMemberBase):
    pass

class ProviderNetworkMemberUpdate(ProviderNetworkMemberBase):
    pass

class ProviderNetworkMemberOut(ProviderNetworkMemberBase):
    id: UUID

    class Config:
        orm_mode = True
