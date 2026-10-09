from __future__ import annotations

from app.parsers.llm_parser import HeuristicParser, OllamaParser

DEMO_QUERY = (
    "sortie scientifique pour 30 \u00e9l\u00e8ves depuis Toulouse "
    "moins de 90 minutes retour avant 18h accessible PMR"
)


def test_heuristic_extracts_demo_query() -> None:
    result = HeuristicParser().parse(DEMO_QUERY)
    assert result.parser == "heuristic"
    assert result.values["origin"] == "Toulouse"
    assert result.values["students"] == 30
    assert result.values["max_travel_time_minutes"] == 90
    assert result.values["return_before"].strftime("%H:%M") == "18:00"
    assert result.values["accessibility"] is True
    assert "science" in result.values["interests"]


def test_heuristic_extracts_hours_form() -> None:
    result = HeuristicParser().parse("from Lyon under 1h30")
    assert result.values["origin"] == "Lyon"
    assert result.values["max_travel_time_minutes"] == 90


def test_heuristic_returns_nothing_without_signals() -> None:
    result = HeuristicParser().parse("bonjour, avez-vous des idees ?")
    assert result.values == {}


def test_llm_failure_falls_back_to_heuristic(monkeypatch) -> None:
    parser = OllamaParser(base_url="http://localhost:1", model="test-model")

    def boom(_query: str) -> str:
        raise RuntimeError("llm unavailable")

    monkeypatch.setattr(parser, "_complete", boom)
    result = parser.parse("30 eleves depuis Toulouse")
    assert result.parser == "heuristic"
    assert result.values["origin"] == "Toulouse"


def test_llm_success_is_tagged_ai_assisted(monkeypatch) -> None:
    parser = OllamaParser(base_url="http://localhost:1", model="test-model")
    monkeypatch.setattr(
        parser,
        "_complete",
        lambda _query: '```json\n{"origin": "Toulouse", "students": 30}\n```',
    )
    result = parser.parse("anything")
    assert result.parser == "ollama"
    assert result.trust.value == "AI-ASSISTED"
    assert result.values["students"] == 30


def test_llm_rejects_unexpected_keys(monkeypatch) -> None:
    parser = OllamaParser(base_url="http://localhost:1", model="test-model")
    monkeypatch.setattr(
        parser,
        "_complete",
        lambda _query: '{"origin": "Toulouse", "is_feasible": true}',
    )
    result = parser.parse("anything")
    assert "is_feasible" not in result.values
