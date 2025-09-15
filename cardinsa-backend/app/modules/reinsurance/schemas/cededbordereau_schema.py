from pydantic import BaseModel, ConfigDict
from typing import Optional

class CededBordereauBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class CededBordereauCreate(CededBordereauBase):
    pass

class CededBordereauUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class CededBordereauRead(CededBordereauBase):
    id: str
