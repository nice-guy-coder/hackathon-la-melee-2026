from __future__ import annotations

from app.engines.confidence_engine import ConfidenceEngine
from app.schemas.rules import Rules


def test_confidence_report_shape(journey_factory, destination_factory) -> None:
    report = ConfidenceEngine().evaluate(journey_factory(), destination_factory(), Rules())
    assert 0.0 <= report.overall <= 100.0
    assert {component.factor for component in report.components} == {
        "reliability",
        "capacity_margin",
        "metadata_completeness",
    }
    assert all(component.trust for component in report.components)


def test_lower_reliability_lowers_confidence(journey_factory, destination_factory) -> None:
    engine = ConfidenceEngine()
    destination = destination_factory()
    high = engine.evaluate(journey_factory(reliability_pct=99), destination, Rules())
    low = engine.evaluate(journey_factory(reliability_pct=40), destination, Rules())
    assert high.overall > low.overall


def test_capacity_margin_tracks_group_size(journey_factory, destination_factory) -> None:
    engine = ConfidenceEngine()
    destination = destination_factory()
    rules = Rules()
    large = engine.evaluate(journey_factory(group_capacity=80), destination, rules)
    small = engine.evaluate(journey_factory(group_capacity=20), destination, rules)
    large_margin = next(c.value for c in large.components if c.factor == "capacity_margin")
    small_margin = next(c.value for c in small.components if c.factor == "capacity_margin")
    assert large_margin > small_margin


def test_metadata_completeness_reflects_missing_data(journey_factory, destination_factory) -> None:
    engine = ConfidenceEngine()
    journey = journey_factory()
    full = engine.evaluate(journey, destination_factory(), Rules())
    empty = engine.evaluate(
        journey,
        destination_factory(themes=[], description=""),
        Rules(),
    )
    full_value = next(c.value for c in full.components if c.factor == "metadata_completeness")
    empty_value = next(c.value for c in empty.components if c.factor == "metadata_completeness")
    assert full_value > empty_value


def test_no_score_is_unexplained(client) -> None:
    body = client.post("/api/search", json={"origin": "Toulouse", "students": 30}).json()
    assert body["recommendations"]
    for recommendation in body["recommendations"]:
        assert recommendation["confidence"]["overall"] == round(
            sum(component["value"] for component in recommendation["confidence"]["components"])
            / len(recommendation["confidence"]["components"]),
            1,
        )
