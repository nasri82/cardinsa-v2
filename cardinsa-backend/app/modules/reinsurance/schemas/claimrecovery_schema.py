from pydantic import BaseModel, ConfigDict
from typing import Optional

class ClaimRecoveryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class ClaimRecoveryCreate(ClaimRecoveryBase):
    pass

class ClaimRecoveryUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class ClaimRecoveryRead(ClaimRecoveryBase):
    id: str
