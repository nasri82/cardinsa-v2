from pydantic import BaseModel, ConfigDict
from typing import Optional

class TreatyReinstatementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TreatyReinstatementCreate(TreatyReinstatementBase):
    pass

class TreatyReinstatementUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TreatyReinstatementRead(TreatyReinstatementBase):
    id: str
