from pydantic import BaseModel, ConfigDict
from typing import Optional

class CessionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class CessionCreate(CessionBase):
    pass

class CessionUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class CessionRead(CessionBase):
    id: str
