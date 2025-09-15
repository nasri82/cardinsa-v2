from pydantic import BaseModel

class PlanBase(BaseModel):
    pass

class PlanCreate(PlanBase):
    pass

class PlanRead(PlanBase):
    id: str | None = None
