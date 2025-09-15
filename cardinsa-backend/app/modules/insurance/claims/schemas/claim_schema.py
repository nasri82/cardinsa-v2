from pydantic import BaseModel

class ClaimBase(BaseModel):
    pass

class ClaimCreate(ClaimBase):
    pass

class ClaimRead(ClaimBase):
    id: str | None = None
