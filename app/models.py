from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Source:
    id: int
    artist_name: str
    source_type: str
    parser_key: str
    source_url: str


@dataclass(slots=True)
class ParsedEvent:
    artist_name: str
    source_url: str
    title: str | None
    event_date_raw: str | None
    event_date: datetime | None
    city: str | None
    venue: str | None
    country: str | None
    source_event_id: str | None = None
    event_url: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)