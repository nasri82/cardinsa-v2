from pydantic import BaseModel

class CompanySubscriptionBase(BaseModel):
    pass

class CompanySubscriptionCreate(CompanySubscriptionBase):
    pass

class CompanySubscriptionRead(CompanySubscriptionBase):
    id: str | None = None
