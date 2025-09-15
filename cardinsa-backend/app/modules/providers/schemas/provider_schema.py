from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from .provider_type_schema import ProviderTypeOut

class ProviderBase(BaseModel):
    name: str
    provider_type_id: UUID
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(ProviderBase):
    pass

class ProviderOut(ProviderBase):
    id: UUID
    provider_type: Optional[ProviderTypeOut] = None

    class Config:
        orm_mode = True
