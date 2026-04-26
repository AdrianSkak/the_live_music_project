from __future__ import annotations

from datetime import datetime, time, timezone

from dateutil import parser as dateutil_parser


def parse_event_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = dateutil_parser.parse(value, fuzzy=True, dayfirst=True)
    except (ValueError, OverflowError):
        return None

    if parsed.tzinfo is None:
        parsed = datetime.combine(parsed.date(), time.min, tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)