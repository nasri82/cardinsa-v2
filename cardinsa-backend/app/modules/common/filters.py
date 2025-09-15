import uuid
from typing import Optional, Tuple
import datetime as dt
from sqlalchemy.sql import ColumnElement

def ilike(column: ColumnElement, term: Optional[str]) -> Optional[ColumnElement]:
    if term is None or term.strip() == "":
        return None
    return column.ilike(f"%{term.strip()}%")

def parse_uuid(s: Optional[str]) -> Optional[uuid.UUID]:
    if not s:
        return None
    return uuid.UUID(s)

def parse_date_range(date_from: Optional[str], date_to: Optional[str]) -> Tuple[Optional[dt.date], Optional[dt.date]]:
    def _parse(x: Optional[str]) -> Optional[dt.date]:
        if not x:
            return None
        return dt.date.fromisoformat(x)
    return _parse(date_from), _parse(date_to)
