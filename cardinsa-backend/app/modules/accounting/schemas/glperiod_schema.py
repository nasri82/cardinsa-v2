from pydantic import BaseModel, ConfigDict
from typing import Optional

class GLPeriodBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class GLPeriodCreate(GLPeriodBase):
    pass

class GLPeriodUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class GLPeriodRead(GLPeriodBase):
    id: str
