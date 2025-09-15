from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ProviderServicePriceBase(BaseModel):
    provider_id: UUID
    service_name: str
    price: float
    currency: Optional[str] = "USD"

class ProviderServicePriceCreate(ProviderServicePriceBase):
    pass

class ProviderServicePriceUpdate(ProviderServicePriceBase):
    pass

class ProviderServicePriceOut(ProviderServicePriceBase):
    id: UUID

    class Config:
        orm_mode = True
