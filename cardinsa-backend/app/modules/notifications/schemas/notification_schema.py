from pydantic import BaseModel

class NotificationBase(BaseModel):
    pass

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: str | None = None
