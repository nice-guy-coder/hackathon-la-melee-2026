from __future__ import annotations

from pydantic import ValidationError

from app.config import Settings
from app.data.base import DataLayer, DataSourceError
from app.engines.confidence_engine import ConfidenceEngine
from app.engines.constraint_engine import ConstraintEngine
from app.engines.explanation_engine import ExplanationEngine
from app.engines.recommendation_engine import RecommendationEngine
from app.parsers.llm_parser import RequestParser
from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.recommendation import (
    CompareRequest,
    CompareResponse,
    Recommendation,
    SearchResponse,
    TrustLevel,
)
from app.schemas.search import SearchRequest


class InputError(ValueError):
    """Raised when a request cannot be interpreted safely."""


class SearchService:
    """Facade that wires parsing, feasibility, scoring and explanations."""

    def __init__(
        self,
        data_layer: DataLayer | None,
        parser: RequestParser,
        settings: Settings,
        constraint_engine: ConstraintEngine | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        confidence_engine: ConfidenceEngine | None = None,
        explanation_engine: ExplanationEngine | None = None,
    ) -> None:
        self._data = data_layer
        self._parser = parser
        self._settings = settings
        self._constraints = constraint_engine or ConstraintEngine()
        self._recommendation = recommendation_engine or RecommendationEngine()
        self._confidence = confidence_engine or ConfidenceEngine()
        self._explanation = explanation_engine or ExplanationEngine()

    def _require_data(self) -> DataLayer:
        if self._data is None:
            raise DataSourceError("The configured data source is unavailable.")
        return self._data

    def _resolve(self, request: SearchRequest) -> tuple[SearchRequest, str, bool]:
        if not request.query:
            return request, "form", False

        parsed = self._parser.parse(request.query)
        merged = request.model_dump()
        for field in parsed.fields:
            if merged.get(field) in (None, "", []) and field in parsed.values:
                merged[field] = parsed.values[field]
        try:
            resolved = SearchRequest(**merged)
        except ValidationError as exc:
            detail = "; ".join(
                f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                for error in exc.errors()[:3]
            )
            raise InputError(f"Request could not be interpreted ({detail}).") from exc
        return resolved, parsed.parser, parsed.trust == TrustLevel.AI_ASSISTED

    def search(self, request: SearchRequest) -> SearchResponse:
        data = self._require_data()
        resolved, extractor, ai_assisted = self._resolve(request)
        rules = data.rules.get_rules()

        recommendations: list[Recommendation] = []
        rejected = 0
        for journey in data.journeys.list_journeys(resolved.origin):
            destination = data.destinations.get_destination(journey.destination_id)
            if destination is None:
                rejected += 1
                continue
            result = self._evaluate(resolved, journey, destination, rules)
            if result.feasible:
                recommendations.append(result)
            else:
                rejected += 1

        recommendations.sort(
            key=lambda item: (-item.trip_score, -item.confidence.overall, item.journey.id)
        )
        feasible_count = len(recommendations)
        recommendations = recommendations[: self._settings.top_n]

        return SearchResponse(
            request=resolved,
            extractor=extractor,
            ai_assisted=ai_assisted,
            data_source=self._settings.data_source,
            feasible_count=feasible_count,
            rejected_count=rejected,
            recommendations=recommendations,
        )

    def compare(self, request: CompareRequest) -> CompareResponse:
        data = self._require_data()
        resolved, _, _ = self._resolve(request.request)
        rules = data.rules.get_rules()

        results: list[Recommendation] = []
        missing: list[str] = []
        for journey_id in request.journey_ids:
            journey = data.journeys.get_journey(journey_id)
            destination = (
                data.destinations.get_destination(journey.destination_id) if journey else None
            )
            if journey is None or destination is None:
                missing.append(journey_id)
                continue
            results.append(self._evaluate(resolved, journey, destination, rules))

        if missing:
            raise InputError(f"Unknown journey ids: {', '.join(missing)}.")
        return CompareResponse(results=results)

    def destinations(self, theme: str | None = None, limit: int = 50) -> list[Destination]:
        data = self._require_data()
        items = data.destinations.list_destinations()
        if theme:
            wanted = theme.casefold()
            items = [
                destination
                for destination in items
                if wanted in {value.casefold() for value in destination.themes}
            ]
        return items[:limit]

    def health(self) -> dict[str, object]:
        loaded = self._data is not None
        return {
            "status": "ok" if loaded else "degraded",
            **self._settings.safe_summary(),
            "data_loaded": loaded,
        }

    def _evaluate(
        self,
        request: SearchRequest,
        journey: Journey,
        destination: Destination,
        rules,
    ) -> Recommendation:
        feasibility = self._constraints.evaluate(request, journey, destination, rules)
        confidence = self._confidence.evaluate(journey, destination, rules)

        if not feasibility.feasible:
            return Recommendation(
                journey=journey,
                destination=destination,
                feasible=False,
                trip_score=0.0,
                confidence=confidence,
                breakdown=[],
                reasons=self._explanation.explain_failure(feasibility),
                violations=feasibility.failed,
            )

        trip_score, breakdown = self._recommendation.score(
            request, journey, destination, rules
        )
        return Recommendation(
            journey=journey,
            destination=destination,
            feasible=True,
            trip_score=trip_score,
            confidence=confidence,
            breakdown=breakdown,
            reasons=self._explanation.explain(feasibility, breakdown, confidence),
            violations=[],
        )
