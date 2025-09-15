from pydantic import BaseModel

class AiTaskBase(BaseModel):
    pass

class AiTaskCreate(AiTaskBase):
    pass

class AiTaskRead(AiTaskBase):
    id: str | None = None
