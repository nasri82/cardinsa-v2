from pydantic import BaseModel

class ProviderNetworkBase(BaseModel):
    pass

class ProviderNetworkCreate(ProviderNetworkBase):
    pass

class ProviderNetworkRead(ProviderNetworkBase):
    id: str | None = None
