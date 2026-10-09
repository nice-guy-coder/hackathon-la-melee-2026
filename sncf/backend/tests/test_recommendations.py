from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.config import Settings
from app.engines.recommendation_engine import DEFAULT_WEIGHTS, RecommendationEngine
from app.main import create_app
from app.schemas.rules import Rules
from app.schemas.search import SearchRequest

DEMO_QUERY = (
    "sortie scientifique pour 30 \u00e9l\u00e8ves depuis Toulouse "
    "moins de 90 minutes retour avant 18h accessible PMR"
)
DEMO_PAYLOAD = {
    "origin": "Toulouse",
    "students": 30,
    "max_travel_time_minutes": 90,
    "return_before": "18:00",
    "accessibility": True,
    "interests": ["science"],
}


def test_search_only_returns_feasible_trips(client: TestClient) -> None:
    response = client.post("/api/search", json=DEMO_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    ids = {item["journey"]["id"] for item in body["recommendations"]}
    assert "tou-carcassonne-1930" not in ids
    assert "tou-albi-0805" not in ids
    assert "tou-espace-small" not in ids
    assert all(item["feasible"] for item in body["recommendations"])
    assert body["rejected_count"] >= 3


def test_demo_natural_language_query(client: TestClient) -> None:
    response = client.post("/api/search", json={"origin": "Toulouse", "query": DEMO_QUERY})
    assert response.status_code == 200
    body = response.json()
    assert body["extractor"] == "heuristic"
    assert body["ai_assisted"] is False
    assert body["request"]["students"] == 30
    assert body["request"]["max_travel_time_minutes"] == 90
    assert body["request"]["return_before"] == "18:00:00"
    assert body["request"]["accessibility"] is True
    top = body["recommendations"][0]
    assert "science" in top["destination"]["themes"]
    assert top["trip_score"] > 0


def test_recommendations_are_trust_tagged(client: TestClient) -> None:
    body = client.post("/api/search", json=DEMO_PAYLOAD).json()
    allowed = {"VERIFIED", "CALCULATED", "AI-ASSISTED"}
    for recommendation in body["recommendations"]:
        assert recommendation["reasons"]
        assert {reason["trust"] for reason in recommendation["reasons"]} <= allowed
        assert {component["trust"] for component in recommendation["breakdown"]} <= allowed
        assert {component["trust"] for component in recommendation["confidence"]["components"]} <= allowed


def test_ranking_is_sorted_by_score(client: TestClient) -> None:
    body = client.post("/api/search", json=DEMO_PAYLOAD).json()
    scores = [item["trip_score"] for item in body["recommendations"]]
    assert scores == sorted(scores, reverse=True)


def test_compare_reports_violations(client: TestClient) -> None:
    response = client.post(
        "/api/compare",
        json={
            "request": {"origin": "Toulouse", "students": 10, "accessibility": True},
            "journey_ids": ["tou-espace-0830", "tou-albi-0805"],
        },
    )
    assert response.status_code == 200
    results = {item["journey"]["id"]: item for item in response.json()["results"]}
    assert results["tou-espace-0830"]["feasible"] is True
    albi = results["tou-albi-0805"]
    assert albi["feasible"] is False
    assert "accessibility_required" in {violation["rule"] for violation in albi["violations"]}
    assert albi["trip_score"] == 0.0


def test_compare_rejects_unknown_ids(client: TestClient) -> None:
    response = client.post(
        "/api/compare",
        json={"request": {"origin": "Toulouse"}, "journey_ids": ["nope", "tou-espace-0830"]},
    )
    assert response.status_code == 422


def test_destinations_endpoint(client: TestClient) -> None:
    response = client.get("/api/destinations", params={"theme": "science"})
    assert response.status_code == 200
    destinations = response.json()
    assert destinations
    assert all("science" in destination["themes"] for destination in destinations)


def test_weights_drive_ranking(journey_factory, destination_factory) -> None:
    engine = RecommendationEngine()
    educational_only = dict.fromkeys(DEFAULT_WEIGHTS, 0.0)
    educational_only["educational_match"] = 1.0
    rules = Rules(weights=educational_only)
    request = SearchRequest(origin="Toulouse", interests=["science"])

    science_score, _ = engine.score(request, journey_factory(), destination_factory(id="d1", themes=["science"]), rules)
    history_score, _ = engine.score(request, journey_factory(), destination_factory(id="d2", themes=["history"]), rules)
    assert science_score > history_score


def test_custom_dataset_is_data_agnostic(tmp_path) -> None:
    destinations = [
        {"id": "d-science", "name": "Science Centre", "city": "Lyon", "themes": ["science"], "accessible": True, "description": "x"},
        {"id": "d-history", "name": "History Centre", "city": "Lyon", "themes": ["history"], "accessible": True, "description": "x"},
    ]
    journey_template = {
        "origin": "Lyon",
        "date": "2026-11-20",
        "departure_time": "08:30",
        "return_time": "17:00",
        "duration_minutes": 30,
        "price_euros": 10.0,
        "reliability_pct": 95,
        "group_capacity": 60,
        "accessible": True,
        "transport": "train",
        "operator": "SNCF",
    }
    journeys = [
        {"id": "j-science", "destination_id": "d-science", **journey_template},
        {"id": "j-history", "destination_id": "d-history", **journey_template},
    ]
    weights = dict.fromkeys(DEFAULT_WEIGHTS, 0.0)
    weights["educational_match"] = 1.0

    (tmp_path / "destinations.json").write_text(json.dumps(destinations), encoding="utf-8")
    (tmp_path / "journeys.json").write_text(json.dumps(journeys), encoding="utf-8")
    (tmp_path / "rules.json").write_text(json.dumps({"weights": weights}), encoding="utf-8")

    settings = Settings(enable_docs=False, allowed_hosts=("testserver",), data_dir=tmp_path)
    with TestClient(create_app(settings)) as test_client:
        body = test_client.post(
            "/api/search", json={"origin": "Lyon", "interests": ["science"]}
        ).json()

    assert body["recommendations"][0]["destination"]["id"] == "d-science"


def test_lower_reliability_lowers_score(journey_factory, destination_factory) -> None:
    engine = RecommendationEngine()
    request = SearchRequest(origin="Toulouse", students=30)
    reliable, _ = engine.score(request, journey_factory(reliability_pct=99), destination_factory(), Rules())
    unreliable, _ = engine.score(request, journey_factory(reliability_pct=40), destination_factory(), Rules())
    assert reliable > unreliable
