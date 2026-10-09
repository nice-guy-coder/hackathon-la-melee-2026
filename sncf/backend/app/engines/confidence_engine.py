from __future__ import annotations

from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.recommendation import (
    ConfidenceComponent,
    ConfidenceReport,
    TrustLevel,
)
from app.schemas.rules import Rules


class ConfidenceEngine:
    """Builds an explainable confidence index from available data."""

    def evaluate(
        self,
        journey: Journey,
        destination: Destination,
        rules: Rules,
    ) -> ConfidenceReport:
        components = [
            ConfidenceComponent(
                factor="reliability",
                value=round(journey.reliability_pct, 1),
                trust=TrustLevel.VERIFIED,
            ),
            ConfidenceComponent(
                factor="capacity_margin",
                value=round(self._capacity_margin(journey, rules), 1),
                trust=TrustLevel.CALCULATED,
            ),
            ConfidenceComponent(
                factor="metadata_completeness",
                value=round(self._metadata_completeness(destination), 1),
                trust=TrustLevel.CALCULATED,
            ),
        ]
        overall = round(sum(component.value for component in components) / len(components), 1)
        return ConfidenceReport(overall=overall, components=components)

    @staticmethod
    def _capacity_margin(journey: Journey, rules: Rules) -> float:
        reference = max(rules.default_max_group_size, 1)
        return max(0.0, min(100.0, 100.0 * journey.group_capacity / reference))

    @staticmethod
    def _metadata_completeness(destination: Destination) -> float:
        signals = [bool(destination.themes), bool(destination.description), bool(destination.city)]
        return 100.0 * sum(signals) / len(signals)
