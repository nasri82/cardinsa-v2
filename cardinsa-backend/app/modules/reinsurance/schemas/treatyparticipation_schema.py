from pydantic import BaseModel, ConfigDict
from typing import Optional

class TreatyParticipationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TreatyParticipationCreate(TreatyParticipationBase):
    pass

class TreatyParticipationUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TreatyParticipationRead(TreatyParticipationBase):
    id: str
