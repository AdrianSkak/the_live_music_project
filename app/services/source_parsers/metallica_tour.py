from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.models import ParsedEvent, Source
from app.services.date_parser import parse_event_datetime
from app.services.source_parsers.base import BaseParser


DATE_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$",
    re.IGNORECASE,
)

EVENT_PATH_RE = re.compile(r"/tour/\d{4}-\d{2}-\d{2}-")

NOISE_EXACT = {
    "BUY TICKETS",
    "More Info",
    "ENHANCED EXPERIENCES SOLD OUT",
    "Enhanced Experiences Sold Out",
    "TRAVEL PACKAGES SOLD OUT",
    "Travel Packages Sold Out",
    "Tickets Sold Out",
    "TICKET SOLD OUT",
    "M72 WORLD TOUR",
    "UPCOMING TOUR DATES",
    "Tour",
}


class MetallicaTourParser(BaseParser):
    def parse(self, html: str, source: Source) -> list[ParsedEvent]:
        soup = BeautifulSoup(html, "html.parser")
        events: list[ParsedEvent] = []
        seen_urls: set[str] = set()

        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "").strip()
            absolute_url = urljoin(source.source_url, href)

            if absolute_url in seen_urls:
                continue

            if not EVENT_PATH_RE.search(urlparse(absolute_url).path):
                continue

            container = self._find_event_container(anchor)
            tokens = self._extract_tokens(container)

            date_raw = next((t for t in tokens if DATE_RE.match(t)), None)
            if not date_raw:
                continue

            location_line = self._find_location_line(tokens, date_raw)
            venue = self._find_venue(tokens, location_line)

            city, country = self._split_location(location_line)

            events.append(
                ParsedEvent(
                    artist_name=source.artist_name,
                    source_url=source.source_url,
                    title="M72 WORLD TOUR",
                    event_date_raw=date_raw,
                    event_date=parse_event_datetime(date_raw),
                    city=city,
                    venue=venue,
                    country=country,
                    source_event_id=absolute_url.rstrip("/"),
                    event_url=absolute_url,
                    raw_payload={
                        "parser": "metallica_tour",
                        "tokens": tokens,
                    },
                )
            )
            seen_urls.add(absolute_url)

        return events

    def _find_event_container(self, element):
        current = element
        best = element

        for _ in range(8):
            if current is None:
                break

            text = current.get_text(" ", strip=True)
            if DATE_RE.search(text) and (
                "More Info" in text or "BUY TICKETS" in text or "Tickets Sold Out" in text
            ):
                best = current

            current = current.parent

        return best

    def _extract_tokens(self, container) -> list[str]:
        tokens = []
        for token in container.stripped_strings:
            cleaned = token.strip()
            if not cleaned:
                continue
            if cleaned in NOISE_EXACT:
                continue
            tokens.append(cleaned)
        return tokens

    def _find_location_line(self, tokens: list[str], date_raw: str | None) -> str | None:
        for token in tokens:
            if token == date_raw:
                continue
            if "," in token and not DATE_RE.match(token):
                return token
        return None

    def _find_venue(self, tokens: list[str], location_line: str | None) -> str | None:
        if not location_line:
            return None

        try:
            index = tokens.index(location_line)
        except ValueError:
            return None

        for token in tokens[index + 1 :]:
            if token in NOISE_EXACT:
                continue
            if DATE_RE.match(token):
                continue
            if "SOLD OUT" in token.upper():
                continue
            return token

        return None

    def _split_location(self, location_line: str | None) -> tuple[str | None, str | None]:
        if not location_line:
            return None, None

        parts = [part.strip() for part in location_line.split(",") if part.strip()]
        if not parts:
            return None, None

        city = parts[0]

        last_part = parts[-1]
        last_words = last_part.split()

        if len(last_words) >= 2 and last_words[0].isupper():
            country = " ".join(last_words[1:])
        else:
            country = last_part

        return city, country