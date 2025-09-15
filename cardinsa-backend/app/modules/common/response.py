from pydantic import BaseModel
from typing import Generic, Optional, TypeVar
T = TypeVar("T")
class Envelope(BaseModel, Generic[T]):
    success: bool; data: Optional[T] = None; error: Optional[str] = None; request_id: Optional[str] = None
def ok(data=None, request_id: str | None = None) -> Envelope: return Envelope(success=True, data=data, request_id=request_id)
def err(message: str, request_id: str | None = None) -> Envelope: return Envelope(success=False, error=message, request_id=request_id)
