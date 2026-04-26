from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import ParsedEvent, Source


class BaseParser(ABC):
    @abstractmethod
    def parse(self, html: str, source: Source) -> list[ParsedEvent]:
        raise NotImplementedError