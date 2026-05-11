from __future__ import annotations

import unittest

from app.models import Source
from app.services.source_parsers.iron_maiden_tour_2026 import IronMaidenTour2026Parser
from app.services.source_parsers.metallica_tour import MetallicaTourParser
from app.services.source_parsers.registry import get_parser


def make_source(artist_name: str, parser_key: str, source_url: str) -> Source:
    return Source(
        id=1,
        artist_name=artist_name,
        source_type="official_site",
        parser_key=parser_key,
        source_url=source_url,
    )


class ParserRegistryTest(unittest.TestCase):
    def test_get_parser_returns_registered_parser(self) -> None:
        parser = get_parser("metallica_tour")

        self.assertIsInstance(parser, MetallicaTourParser)

    def test_get_parser_rejects_unknown_parser_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "Brak parsera"):
            get_parser("unknown_parser")


class MetallicaTourParserTest(unittest.TestCase):
    def test_parse_extracts_event_from_tour_link(self) -> None:
        source = make_source(
            artist_name="Metallica",
            parser_key="metallica_tour",
            source_url="https://www.metallica.com/tour",
        )
        html = """
        <section>
            <article>
                <a href="/tour/2026-06-01-warsaw-poland">More Info</a>
                <span>June 1, 2026</span>
                <span>Warsaw, Poland</span>
                <span>PGE Narodowy</span>
                <span>BUY TICKETS</span>
            </article>
        </section>
        """

        events = MetallicaTourParser().parse(html, source)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.artist_name, "Metallica")
        self.assertEqual(event.city, "Warsaw")
        self.assertEqual(event.country, "Poland")
        self.assertEqual(event.venue, "PGE Narodowy")
        self.assertEqual(event.source_event_id, "https://www.metallica.com/tour/2026-06-01-warsaw-poland")
        self.assertEqual(event.event_url, "https://www.metallica.com/tour/2026-06-01-warsaw-poland")
        self.assertIsNotNone(event.event_date)

    def test_parse_ignores_empty_html(self) -> None:
        source = make_source("Metallica", "metallica_tour", "https://www.metallica.com/tour")

        events = MetallicaTourParser().parse("", source)

        self.assertEqual(events, [])


class IronMaidenTour2026ParserTest(unittest.TestCase):
    def test_parse_extracts_event_from_tour_page_tokens(self) -> None:
        source = make_source(
            artist_name="Iron Maiden",
            parser_key="iron_maiden_tour_2026",
            source_url="https://www.ironmaiden.com/tour/run-for-your-lives-world-tour-2026/",
        )
        html = """
        <main>
            <h1>Run For Your Lives World Tour 2026</h1>
            <h2>June 2026</h2>
            <div>3 Jun 2026</div>
            <div>Warsaw, Poland</div>
            <div>PGE Narodowy</div>
            <a>More Info</a>
        </main>
        """

        events = IronMaidenTour2026Parser().parse(html, source)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.artist_name, "Iron Maiden")
        self.assertEqual(event.city, "Warsaw")
        self.assertEqual(event.country, "Poland")
        self.assertEqual(event.venue, "PGE Narodowy")
        self.assertEqual(event.event_url, source.source_url)
        self.assertIsNotNone(event.source_event_id)
        self.assertIsNotNone(event.event_date)

    def test_parse_ignores_content_before_tour_title(self) -> None:
        source = make_source(
            "Iron Maiden",
            "iron_maiden_tour_2026",
            "https://www.ironmaiden.com/tour/run-for-your-lives-world-tour-2026/",
        )
        html = """
        <main>
            <div>1 Jan 2026</div>
            <div>Noise City, Nowhere</div>
        </main>
        """

        events = IronMaidenTour2026Parser().parse(html, source)

        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
