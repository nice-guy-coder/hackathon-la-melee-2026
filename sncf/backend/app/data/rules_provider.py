from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from app.data.base import DataSourceError, RulesRepository
from app.schemas.rules import Rules


class JsonRulesRepository(RulesRepository):
    """Adapter that reads scoring and pricing rules from a JSON dataset."""

    def __init__(self, data_dir: Path, filename: str = "rules.json") -> None:
        self._rules = self._load(data_dir / filename)

    @staticmethod
    def _load(path: Path) -> Rules:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise DataSourceError(f"Rules dataset not found: {path.name}") from exc
        except json.JSONDecodeError as exc:
            raise DataSourceError(f"Rules dataset is not valid JSON: {path.name}") from exc
        try:
            return Rules.model_validate(raw)
        except ValidationError as exc:
            raise DataSourceError(f"Rules dataset failed validation: {path.name}") from exc

    def get_rules(self) -> Rules:
        return self._rules
