from pydantic import BaseModel, ConfigDict
from typing import Optional

class GLEntryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class GLEntryCreate(GLEntryBase):
    pass

class GLEntryUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class GLEntryRead(GLEntryBase):
    id: str
