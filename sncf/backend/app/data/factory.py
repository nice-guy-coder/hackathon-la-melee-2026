from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.config import Settings
from app.data.base import DataLayer, DataSourceError
from app.data.destination_provider import JsonDestinationRepository
from app.data.rules_provider import JsonRulesRepository
from app.data.sncf_provider import JsonJourneyRepository

ProviderBuilder = Callable[[Path], DataLayer]

_REGISTRY: dict[str, ProviderBuilder] = {}


def register_data_source(name: str, builder: ProviderBuilder) -> None:
    _REGISTRY[name.casefold()] = builder


def _build_mock(data_dir: Path) -> DataLayer:
    return DataLayer(
        journeys=JsonJourneyRepository(data_dir),
        destinations=JsonDestinationRepository(data_dir),
        rules=JsonRulesRepository(data_dir),
    )


def create_data_layer(settings: Settings) -> DataLayer:
    builder = _REGISTRY.get(settings.data_source.casefold())
    if builder is None:
        raise DataSourceError(f"Unsupported data source: {settings.data_source}")
    return builder(settings.data_dir)


register_data_source("mock", _build_mock)
