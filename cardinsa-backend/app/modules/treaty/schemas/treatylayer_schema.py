from pydantic import BaseModel, ConfigDict
from typing import Optional

class TreatyLayerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TreatyLayerCreate(TreatyLayerBase):
    pass

class TreatyLayerUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TreatyLayerRead(TreatyLayerBase):
    id: str
