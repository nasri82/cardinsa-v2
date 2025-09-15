from pydantic import BaseModel

class DocumentBase(BaseModel):
    pass

class DocumentCreate(DocumentBase):
    pass

class DocumentRead(DocumentBase):
    id: str | None = None
