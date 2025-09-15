from pydantic import BaseModel

class SaaSPlanBase(BaseModel):
    pass

class SaaSPlanCreate(SaaSPlanBase):
    pass

class SaaSPlanRead(SaaSPlanBase):
    id: str | None = None
