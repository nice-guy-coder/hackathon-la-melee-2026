from __future__ import annotations

from datetime import date, time

import pytest

from app.engines.constraint_engine import ConstraintEngine
from app.schemas.recommendation import TrustLevel
from app.schemas.rules import Rules
from app.schemas.search import SearchRequest

VIOLATION_CASES = [
    ({"origin": "Bordeaux"}, {}, "origin_matches"),
    ({"date": date(2026, 11, 21)}, {}, "date_matches"),
    ({"max_travel_time_minutes": 10}, {}, "duration_limit"),
    ({"max_budget_euros": 5}, {}, "budget_limit"),
    ({"return_before": time(16, 0)}, {}, "return_before"),
    ({"accessibility": True}, {"accessible": False}, "accessibility_required"),
    ({"students": 100}, {}, "group_capacity"),
    ({"transport": "bus"}, {}, "transport_mode"),
]


def _request(**overrides) -> SearchRequest:
    data = {
        "origin": "Toulouse",
        "students": 30,
        "accessibility": True,
        "max_travel_time_minutes": 90,
        "return_before": time(18, 0),
    }
    data.update(overrides)
    return SearchRequest(**data)


def test_all_constraints_pass(journey_factory, destination_factory) -> None:
    report = ConstraintEngine().evaluate(
        _request(),
        journey_factory(),
        destination_factory(),
        Rules(),
    )
    assert report.feasible is True
    assert report.failed == []
    assert len(report.checks) == 8


@pytest.mark.parametrize("request_overrides, journey_overrides, expected_rule", VIOLATION_CASES)
def test_constraint_violation_is_reported(
    request_overrides,
    journey_overrides,
    expected_rule,
    journey_factory,
    destination_factory,
) -> None:
    report = ConstraintEngine().evaluate(
        _request(**request_overrides),
        journey_factory(**journey_overrides),
        destination_factory(),
        Rules(),
    )
    assert report.feasible is False
    assert expected_rule in {check.rule for check in report.failed}


def test_every_check_has_a_trust_level(journey_factory, destination_factory) -> None:
    report = ConstraintEngine().evaluate(
        _request(),
        journey_factory(),
        destination_factory(),
        Rules(),
    )
    for check in report.checks:
        assert isinstance(check.trust, TrustLevel)
        assert check.message
