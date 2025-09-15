from __future__ import annotations
from typing import Iterable, Optional
from sqlalchemy.sql import ColumnElement, and_, or_
from sqlalchemy import func
def like_or_ilike(column, term: Optional[str], case_insensitive: bool = True):
    if not term: return None
    term = f"%{term.strip()}%"; return column.ilike(term) if case_insensitive else column.like(term)
def in_(column, values: Optional[Iterable]):
    if not values: return None
    return column.in_(list(values))
def between(column, low, high):
    if low is None and high is None: return None
    if low is None: return column <= high
    if high is None: return column >= low
    return column.between(low, high)
def coalesce_date(date_col, fallback=None): return func.coalesce(date_col, fallback) if fallback is not None else date_col
def all_filters(*clauses: Optional[ColumnElement]):
    filtered = [c for c in clauses if c is not None]; return and_(*filtered) if filtered else None
def any_filters(*clauses: Optional[ColumnElement]):
    filtered = [c for c in clauses if c is not None]; return or_(*filtered) if filtered else None
