from datetime import datetime, date, timezone

FMT = "%d/%m/%Y"

def parse_br_date(s: str) -> date:
    return datetime.strptime(s, FMT).date()

def format_br_date(d: date) -> str:
    return d.strftime(FMT)

def now_utc() -> datetime:
    return datetime.now(timezone.utc)
