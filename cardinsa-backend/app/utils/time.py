import datetime as dt
from typing import Optional

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

def parse_iso_datetime(value: str) -> dt.datetime:
    # Accept 'YYYY-MM-DD' or full ISO
    try:
        if len(value) == 10:
            return dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc)
        dtv = dt.datetime.fromisoformat(value)
        if dtv.tzinfo is None:
            dtv = dtv.replace(tzinfo=dt.timezone.utc)
        return dtv.astimezone(dt.timezone.utc)
    except Exception as e:
        raise ValueError(f"Invalid ISO datetime: {value}") from e

def start_of_day_utc(d: dt.date | dt.datetime) -> dt.datetime:
    if isinstance(d, dt.datetime):
        d = d.date()
    return dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc)

def end_of_day_utc(d: dt.date | dt.datetime) -> dt.datetime:
    sod = start_of_day_utc(d)
    return sod + dt.timedelta(days=1) - dt.timedelta(microseconds=1)
