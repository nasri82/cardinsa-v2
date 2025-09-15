from pydantic import BaseModel

class QuotationBase(BaseModel):
    pass

class QuotationCreate(QuotationBase):
    pass

class QuotationRead(QuotationBase):
    id: str | None = None
