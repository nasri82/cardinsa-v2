# app/common/pagination.py
from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")

class PageMeta(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int = 0

class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

def paginate(db: Session, stmt, page: int = 1, page_size: int = 20) -> tuple[int, Sequence]:
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)))
    return total, items
