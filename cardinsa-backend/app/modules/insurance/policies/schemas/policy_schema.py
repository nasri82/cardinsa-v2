from pydantic import BaseModel

class PolicyBase(BaseModel):
    pass

class PolicyCreate(PolicyBase):
    pass

class PolicyRead(PolicyBase):
    id: str | None = None
