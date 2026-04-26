from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup

from app.models import ParsedEvent, Source
from app.services.date_parser import parse_event_datetime
from app.services.source_parsers.base import BaseParser


DATE_RE = re.compile(
    r"^\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
    r"January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$",
    re.IGNORECASE,
)

MONTH_HEADING_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$",
    re.IGNORECASE,
)

NOISE_EXACT = {
    "Filter",
    "On Sale",
}

STOP_MARKERS = {
    "More Info",
    "Sold Out",
}


class IronMaidenTour2026Parser(BaseParser):
    def parse(self, html: str, source: Source) -> list[ParsedEvent]:
        soup = BeautifulSoup(html, "html.parser")
        tokens = self._extract_tokens(soup)
        events: list[ParsedEvent] = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if not DATE_RE.match(token):
                i += 1
                continue

            date_raw = token
            location = self._next_meaningful_token(tokens, i + 1)
            venue = self._next_meaningful_token(tokens, i + 2)

            city, country = self._split_location(location)

            source_event_id = hashlib.md5(
                f"{source.parser_key}|{date_raw}|{location}|{venue}".encode("utf-8")
            ).hexdigest()

            events.append(
                ParsedEvent(
                    artist_name=source.artist_name,
                    source_url=source.source_url,
                    title="Run For Your Lives World Tour 2026",
                    event_date_raw=date_raw,
                    event_date=parse_event_datetime(date_raw),
                    city=city,
                    venue=venue,
                    country=country,
                    source_event_id=source_event_id,
                    event_url=source.source_url,
                    raw_payload={
                        "parser": "iron_maiden_tour_2026",
                        "location_raw": location,
                        "venue_raw": venue,
                    },
                )
            )

            i += 1

        return events

    def _extract_tokens(self, soup: BeautifulSoup) -> list[str]:
        raw_tokens = [token.strip() for token in soup.stripped_strings]
        cleaned: list[str] = []

        seen_title = False
        for token in raw_tokens:
            if token == "Run For Your Lives World Tour 2026":
                seen_title = True
                cleaned.append(token)
                continue

            if not seen_title:
                continue

            if not token:
                continue

            if token in NOISE_EXACT:
                continue

            cleaned.append(token)

        return cleaned

    def _next_meaningful_token(self, tokens: list[str], start_index: int) -> str | None:
        for token in tokens[start_index:]:
            if DATE_RE.match(token):
                return None
            if MONTH_HEADING_RE.match(token):
                continue
            if token in NOISE_EXACT:
                continue
            if token in STOP_MARKERS:
                continue
            return token
        return None

    def _split_location(self, value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None

        parts = [part.strip() for part in value.split(",") if part.strip()]
        if not parts:
            return None, None

        if len(parts) == 1:
            return parts[0], None

        city = parts[0]
        country = parts[-1]
        return city, country