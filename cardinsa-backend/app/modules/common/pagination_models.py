from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="1-based page index")
    size: int = Field(20, ge=1, le=100, description="page size (max 100)")
    sort_by: Optional[str] = Field(None, description="Model attribute to sort by")
    sort_dir: Optional[str] = Field("asc", description="'asc' or 'desc'")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PageMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int

class Page(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta
