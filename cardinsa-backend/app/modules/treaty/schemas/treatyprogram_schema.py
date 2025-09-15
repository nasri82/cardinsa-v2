from pydantic import BaseModel, ConfigDict
from typing import Optional

class TreatyProgramBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class TreatyProgramCreate(TreatyProgramBase):
    pass

class TreatyProgramUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class TreatyProgramRead(TreatyProgramBase):
    id: str
