from app.services.source_parsers.base import BaseParser
from app.services.source_parsers.metallica_tour import MetallicaTourParser
from app.services.source_parsers.iron_maiden_tour_2026 import IronMaidenTour2026Parser


PARSERS: dict[str, BaseParser] = {
    "metallica_tour": MetallicaTourParser(),
    "iron_maiden_tour_2026": IronMaidenTour2026Parser(),
}


def get_parser(parser_key: str) -> BaseParser:
    try:
        return PARSERS[parser_key]
    except KeyError as exc:
        raise ValueError(f"Brak parsera dla parser_key={parser_key}") from exc