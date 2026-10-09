from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.data.base import DataSourceError, DestinationRepository
from app.schemas.destination import Destination

_DESTINATION_LIST = TypeAdapter(list[Destination])


class JsonDestinationRepository(DestinationRepository):
    """Adapter that reads destinations from a JSON dataset."""

    def __init__(self, data_dir: Path, filename: str = "destinations.json") -> None:
        self._destinations = self._load(data_dir / filename)

    @staticmethod
    def _load(path: Path) -> list[Destination]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise DataSourceError(f"Destination dataset not found: {path.name}") from exc
        except json.JSONDecodeError as exc:
            raise DataSourceError(f"Destination dataset is not valid JSON: {path.name}") from exc
        try:
            return _DESTINATION_LIST.validate_python(raw)
        except ValidationError as exc:
            raise DataSourceError(f"Destination dataset failed validation: {path.name}") from exc

    def list_destinations(self) -> list[Destination]:
        return list(self._destinations)

    def get_destination(self, destination_id: str) -> Destination | None:
        for destination in self._destinations:
            if destination.id == destination_id:
                return destination
        return None
