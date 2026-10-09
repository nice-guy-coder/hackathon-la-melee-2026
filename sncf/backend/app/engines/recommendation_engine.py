from __future__ import annotations

from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.recommendation import ScoreComponent, TrustLevel
from app.schemas.rules import Rules
from app.schemas.search import SearchRequest

DEFAULT_WEIGHTS: dict[str, float] = {
    "educational_match": 0.30,
    "reliability": 0.20,
    "journey_simplicity": 0.20,
    "group_suitability": 0.15,
    "cost": 0.10,
    "accessibility": 0.05,
}

FACTOR_LABELS: dict[str, str] = {
    "educational_match": "educational match",
    "reliability": "reliability",
    "journey_simplicity": "journey simplicity",
    "group_suitability": "group suitability",
    "cost": "cost",
    "accessibility": "accessibility",
}

_SIMPLICITY_REFERENCE_MINUTES = 180.0
_COST_REFERENCE_EUROS = 50.0


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


class RecommendationEngine:
    """Scores feasible journeys with configurable weighted factors."""

    def __init__(self, default_weights: dict[str, float] | None = None) -> None:
        self._defaults = dict(default_weights or DEFAULT_WEIGHTS)

    def effective_weights(self, rules: Rules) -> dict[str, float]:
        weights = dict(self._defaults)
        for factor, weight in rules.weights.items():
            if factor in weights:
                weights[factor] = _clamp(weight, 0.0, 1.0)
        return weights

    def score(
        self,
        request: SearchRequest,
        journey: Journey,
        destination: Destination,
        rules: Rules,
    ) -> tuple[float, list[ScoreComponent]]:
        weights = self.effective_weights(rules)
        factor_scores = self._factor_scores(request, journey, destination, rules)
        total_weight = sum(weights[factor] for factor in factor_scores) or 1.0

        components: list[ScoreComponent] = []
        weighted_total = 0.0
        for factor, score in factor_scores.items():
            weight = weights[factor]
            weighted_score = round(_clamp(score) * weight, 3)
            weighted_total += weighted_score
            components.append(
                ScoreComponent(
                    factor=factor,
                    score=round(_clamp(score), 1),
                    weight=round(weight, 3),
                    weighted_score=weighted_score,
                    trust=self._trust(factor),
                )
            )

        return round(weighted_total / total_weight, 1), components

    @staticmethod
    def _trust(factor: str) -> TrustLevel:
        if factor in {"reliability", "accessibility"}:
            return TrustLevel.VERIFIED
        return TrustLevel.CALCULATED

    def _factor_scores(
        self,
        request: SearchRequest,
        journey: Journey,
        destination: Destination,
        rules: Rules,
    ) -> dict[str, float]:
        return {
            "educational_match": _educational_match(request, destination),
            "reliability": journey.reliability_pct,
            "journey_simplicity": _clamp(
                100.0 * (1.0 - journey.duration_minutes / _SIMPLICITY_REFERENCE_MINUTES)
            ),
            "group_suitability": _group_suitability(request, journey),
            "cost": _clamp(
                100.0
                * (
                    1.0
                    - rules.student_price(journey.price_euros, request.students)
                    / _COST_REFERENCE_EUROS
                )
            ),
            "accessibility": _accessibility(request, journey, destination),
        }


def _educational_match(request: SearchRequest, destination: Destination) -> float:
    if not request.interests:
        return 50.0
    wanted = {interest.casefold() for interest in request.interests}
    themes = {theme.casefold() for theme in destination.themes}
    matched = wanted & themes
    return _clamp(100.0 * len(matched) / len(wanted))


def _group_suitability(request: SearchRequest, journey: Journey) -> float:
    if request.students is None:
        return 50.0
    return _clamp(50.0 + 2.0 * (journey.group_capacity - request.students))


def _accessibility(request: SearchRequest, journey: Journey, destination: Destination) -> float:
    both_accessible = journey.accessible and destination.accessible
    if request.accessibility:
        return 100.0 if both_accessible else 0.0
    return 75.0 if both_accessible else 50.0
