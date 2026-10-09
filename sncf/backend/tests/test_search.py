import pytest
from pydantic import ValidationError

from app.schemas.search import SearchRequest


def test_valid_search_request():
    request = SearchRequest(
        origin="Toulouse",
        max_budget_euros=30,
        max_travel_time_minutes=120,
        interests=["history", "culture"],
        accessibility=True,
        transport="train",
    )

    assert request.origin == "Toulouse"
    assert request.max_budget_euros == 30
    assert request.max_travel_time_minutes == 120
    assert request.interests == ["history", "culture"]
    assert request.accessibility is True
    assert request.transport == "train"


def test_minimal_search_request():
    request = SearchRequest(
        origin="Toulouse"
    )

    assert request.origin == "Toulouse"
    assert request.max_budget_euros is None
    assert request.max_travel_time_minutes is None
    assert request.interests == []
    assert request.accessibility is None
    assert request.transport == "train"


def test_negative_budget_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(
            origin="Toulouse",
            max_budget_euros=-10,
        )


def test_negative_travel_time_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(
            origin="Toulouse",
            max_travel_time_minutes=-30,
        )


def test_empty_origin_rejected():
    with pytest.raises(ValidationError):
        SearchRequest(
            origin=""
        )