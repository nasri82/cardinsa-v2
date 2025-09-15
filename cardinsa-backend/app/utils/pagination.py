from math import ceil
from typing import Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.modules.common.pagination_models import PageParams, PageMeta

def paginate(db: Session, stmt: Select, params: PageParams) -> Tuple[list, PageMeta]:
    # Count total
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.execute(count_stmt).scalar_one()
    # Fetch page
    page_stmt = stmt.limit(params.size).offset(params.offset)
    rows = db.execute(page_stmt).scalars().all()
    meta = PageMeta(
        page=params.page,
        size=params.size,
        total=total,
        pages=ceil(total / params.size) if params.size else 0,
    )
    return rows, meta

def apply_sort(stmt: Select, model, sort_by: str | None, sort_dir: str | None) -> Select:
    if not sort_by:
        return stmt
    col = getattr(model, sort_by, None)
    if col is None:
        return stmt
    if (sort_dir or "asc").lower() == "desc":
        return stmt.order_by(col.desc())
    return stmt.order_by(col.asc())
