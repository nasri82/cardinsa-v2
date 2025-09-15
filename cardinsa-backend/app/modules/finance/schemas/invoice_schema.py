from pydantic import BaseModel

class InvoiceBase(BaseModel):
    pass

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceRead(InvoiceBase):
    id: str | None = None
