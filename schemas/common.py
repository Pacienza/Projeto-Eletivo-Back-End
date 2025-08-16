from marshmallow import fields, ValidationError
from datetime import datetime, date, time

_FMT = "%d/%m/%Y"

def _parse_br_date(s: str) -> date:
    return datetime.strptime(s, _FMT).date()

def _format_br_date(d: date) -> str:
    return d.strftime(_FMT)

class DateDDMMYYYY(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return _format_br_date(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return _parse_br_date(value)
        except Exception:
            raise ValidationError("Use o formato dd/mm/aaaa")
class TimeHHMM(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.strftime("%H:%M")
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            hh, mm = value.split(":")
            return time(hour=int(hh), minute=int(mm))
        except Exception:
            raise ValidationError("Use o formato HH:MM (24h)")