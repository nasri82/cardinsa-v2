from fastapi import Query
from app.modules.common.pagination_models import PageParams

def page_params(
    page: int = Query(1, ge=1, description="1-based page index"),
    size: int = Query(20, ge=1, le=100, description="page size"),
    sort_by: str | None = Query(None, description="sort column"),
    sort_dir: str | None = Query("asc", pattern="^(?i)(asc|desc)$", description="asc or desc"),
) -> PageParams:
    return PageParams(page=page, size=size, sort_by=sort_by, sort_dir=sort_dir)
