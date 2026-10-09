from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.data.base import DataSourceError, JourneyRepository
from app.schemas.journey import Journey

_JOURNEY_LIST = TypeAdapter(list[Journey])


class JsonJourneyRepository(JourneyRepository):
    """Adapter that reads journeys from a JSON dataset."""

    def __init__(self, data_dir: Path, filename: str = "journeys.json") -> None:
        self._journeys = self._load(data_dir / filename)

    @staticmethod
    def _load(path: Path) -> list[Journey]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise DataSourceError(f"Journey dataset not found: {path.name}") from exc
        except json.JSONDecodeError as exc:
            raise DataSourceError(f"Journey dataset is not valid JSON: {path.name}") from exc
        try:
            return _JOURNEY_LIST.validate_python(raw)
        except ValidationError as exc:
            raise DataSourceError(f"Journey dataset failed validation: {path.name}") from exc

    def list_journeys(self, origin: str | None = None) -> list[Journey]:
        if origin is None:
            return list(self._journeys)
        wanted = origin.casefold()
        return [journey for journey in self._journeys if journey.origin.casefold() == wanted]

    def get_journey(self, journey_id: str) -> Journey | None:
        for journey in self._journeys:
            if journey.id == journey_id:
                return journey
        return None
