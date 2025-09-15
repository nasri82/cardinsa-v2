from pydantic import BaseModel, ConfigDict
from typing import Optional

class TreatyContractBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TreatyContractCreate(TreatyContractBase):
    pass

class TreatyContractUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TreatyContractRead(TreatyContractBase):
    id: str
