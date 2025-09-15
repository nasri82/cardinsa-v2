from pydantic import BaseModel, ConfigDict
from typing import Optional

class GLAccountBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class GLAccountCreate(GLAccountBase):
    pass

class GLAccountUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class GLAccountRead(GLAccountBase):
    id: str
