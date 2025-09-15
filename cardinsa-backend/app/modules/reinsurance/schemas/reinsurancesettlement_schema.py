from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReinsuranceSettlementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class ReinsuranceSettlementCreate(ReinsuranceSettlementBase):
    pass

class ReinsuranceSettlementUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class ReinsuranceSettlementRead(ReinsuranceSettlementBase):
    id: str
