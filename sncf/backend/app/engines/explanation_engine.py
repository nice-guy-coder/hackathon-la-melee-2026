from __future__ import annotations

from app.engines.recommendation_engine import FACTOR_LABELS
from app.schemas.recommendation import (
    ConfidenceReport,
    FeasibilityReport,
    Reason,
    ScoreComponent,
    TrustLevel,
)

_MAX_CHECK_REASONS = 5
_MAX_FACTOR_REASONS = 2


class ExplanationEngine:
    """Turns engine outputs into traceable, human-readable reasons."""

    def explain(
        self,
        feasibility: FeasibilityReport,
        breakdown: list[ScoreComponent],
        confidence: ConfidenceReport,
    ) -> list[Reason]:
        reasons: list[Reason] = []
        for check in feasibility.passed[:_MAX_CHECK_REASONS]:
            reasons.append(Reason(label=check.rule, detail=check.message, trust=check.trust))

        top_factors = sorted(breakdown, key=lambda item: item.weighted_score, reverse=True)
        for component in top_factors[:_MAX_FACTOR_REASONS]:
            label = FACTOR_LABELS.get(component.factor, component.factor)
            reasons.append(
                Reason(
                    label=label,
                    detail=(
                        f"{label.capitalize()} scores {component.score:.0f}/100 "
                        f"with weight {component.weight:.0%}."
                    ),
                    trust=component.trust,
                )
            )

        summary = "; ".join(
            f"{FACTOR_LABELS.get(item.factor, item.factor)} {item.value:.0f}"
            for item in confidence.components
        )
        reasons.append(
            Reason(
                label="confidence",
                detail=f"Confidence index is {confidence.overall:.0f}/100 based on {summary}.",
                trust=TrustLevel.CALCULATED,
            )
        )
        return reasons

    def explain_failure(self, feasibility: FeasibilityReport) -> list[Reason]:
        return [
            Reason(label=check.rule, detail=check.message, trust=check.trust)
            for check in feasibility.failed
        ]
