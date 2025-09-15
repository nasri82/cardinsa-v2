from pydantic import BaseModel, ConfigDict
from typing import Optional

class GLJournalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # TODO: add real fields aligned with DB schema

class GLJournalCreate(GLJournalBase):
    pass

class GLJournalUpdate(BaseModel):
    # TODO: add updatable fields
    pass

class GLJournalRead(GLJournalBase):
    id: str
