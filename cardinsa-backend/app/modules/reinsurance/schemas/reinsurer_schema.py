from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReinsurerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class ReinsurerCreate(ReinsurerBase):
    pass

class ReinsurerUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class ReinsurerRead(ReinsurerBase):
    id: str
