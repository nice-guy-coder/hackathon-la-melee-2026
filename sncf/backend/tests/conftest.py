from __future__ import annotations

from datetime import date, time

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.schemas.destination import Destination
from app.schemas.journey import Journey


@pytest.fixture()
def settings() -> Settings:
    return Settings(enable_docs=False, allowed_hosts=("localhost", "testserver"))


@pytest.fixture()
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture()
def journey_factory():
    def _make(**overrides) -> Journey:
        data = {
            "id": "j1",
            "origin": "Toulouse",
            "destination_id": "d1",
            "date": date(2026, 11, 20),
            "departure_time": time(8, 30),
            "return_time": time(17, 0),
            "duration_minutes": 30,
            "price_euros": 10.0,
            "reliability_pct": 95,
            "group_capacity": 60,
            "accessible": True,
            "transport": "train",
            "operator": "SNCF",
        }
        data.update(overrides)
        return Journey(**data)

    return _make


@pytest.fixture()
def destination_factory():
    def _make(**overrides) -> Destination:
        data = {
            "id": "d1",
            "name": "Science Museum",
            "city": "Toulouse",
            "themes": ["science"],
            "accessible": True,
            "description": "A science museum.",
        }
        data.update(overrides)
        return Destination(**data)

    return _make
