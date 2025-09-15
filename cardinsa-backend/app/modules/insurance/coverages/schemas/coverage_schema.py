from pydantic import BaseModel

class CoverageBase(BaseModel):
    pass

class CoverageCreate(CoverageBase):
    pass

class CoverageRead(CoverageBase):
    id: str | None = None
