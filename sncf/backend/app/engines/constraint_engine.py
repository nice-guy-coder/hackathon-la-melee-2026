from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.recommendation import CheckResult, FeasibilityReport, TrustLevel
from app.schemas.rules import Rules
from app.schemas.search import SearchRequest


class Constraint(ABC):
    """Specification that decides whether one requirement is satisfied."""

    rule: str
    trust: TrustLevel

    @abstractmethod
    def check(
        self,
        request: SearchRequest,
        journey: Journey,
        destination: Destination,
        rules: Rules,
    ) -> CheckResult:
        raise NotImplementedError

    def _result(self, satisfied: bool, message: str) -> CheckResult:
        return CheckResult(
            rule=self.rule,
            satisfied=satisfied,
            message=message,
            trust=self.trust,
        )


class OriginMatches(Constraint):
    rule = "origin_matches"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if not request.origin:
            return self._result(False, "No departure origin was provided.")
        if journey.origin.casefold() == request.origin.casefold():
            return self._result(True, f"Departs from {journey.origin}.")
        return self._result(False, f"Departs from {journey.origin}, not {request.origin}.")


class DateMatches(Constraint):
    rule = "date_matches"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if request.date is None:
            return self._result(True, f"Scheduled on {journey.date.isoformat()}.")
        if journey.date == request.date:
            return self._result(True, f"Runs on the requested date {journey.date.isoformat()}.")
        return self._result(False, f"Runs on {journey.date.isoformat()}, not {request.date.isoformat()}.")


class DurationLimit(Constraint):
    rule = "duration_limit"
    trust = TrustLevel.CALCULATED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if request.max_travel_time_minutes is None:
            return self._result(True, f"Travel time is {journey.duration_minutes} minutes.")
        if journey.duration_minutes <= request.max_travel_time_minutes:
            return self._result(
                True,
                f"Travel time of {journey.duration_minutes} minutes is within the {request.max_travel_time_minutes} minute limit.",
            )
        return self._result(
            False,
            f"Travel time of {journey.duration_minutes} minutes exceeds the {request.max_travel_time_minutes} minute limit.",
        )


class BudgetLimit(Constraint):
    rule = "budget_limit"
    trust = TrustLevel.CALCULATED

    def check(self, request, journey, destination, rules) -> CheckResult:
        price = rules.student_price(journey.price_euros, request.students)
        if request.max_budget_euros is None:
            return self._result(True, f"Estimated price is {price} EUR per student.")
        if price <= request.max_budget_euros:
            return self._result(True, f"Price of {price} EUR per student fits the budget.")
        return self._result(
            False,
            f"Price of {price} EUR per student exceeds the {request.max_budget_euros} EUR budget.",
        )


class ReturnBefore(Constraint):
    rule = "return_before"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if request.return_before is None:
            return self._result(True, f"Returns at {journey.return_time.strftime('%H:%M')}.")
        if journey.return_time <= request.return_before:
            return self._result(
                True,
                f"Return at {journey.return_time.strftime('%H:%M')} is before {request.return_before.strftime('%H:%M')}.",
            )
        return self._result(
            False,
            f"Return at {journey.return_time.strftime('%H:%M')} is after {request.return_before.strftime('%H:%M')}.",
        )


class AccessibilityRequired(Constraint):
    rule = "accessibility_required"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if not request.accessibility:
            return self._result(True, "Accessibility was not requested.")
        if journey.accessible and destination.accessible:
            return self._result(True, "Travel and destination are both accessible.")
        missing = []
        if not journey.accessible:
            missing.append("travel")
        if not destination.accessible:
            missing.append("destination")
        return self._result(False, f"Accessibility is not guaranteed for {' and '.join(missing)}.")


class GroupCapacity(Constraint):
    rule = "group_capacity"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if request.students is None:
            return self._result(True, f"Group capacity is {journey.group_capacity} seats.")
        if journey.group_capacity >= request.students:
            return self._result(
                True,
                f"Capacity of {journey.group_capacity} seats covers the {request.students} students.",
            )
        return self._result(
            False,
            f"Capacity of {journey.group_capacity} seats is below the {request.students} students.",
        )


class TransportMode(Constraint):
    rule = "transport_mode"
    trust = TrustLevel.VERIFIED

    def check(self, request, journey, destination, rules) -> CheckResult:
        if journey.transport.casefold() == request.transport.casefold():
            return self._result(True, f"Uses the requested transport mode {request.transport}.")
        return self._result(False, f"Uses {journey.transport}, not {request.transport}.")


DEFAULT_CONSTRAINTS: tuple[Constraint, ...] = (
    OriginMatches(),
    DateMatches(),
    DurationLimit(),
    BudgetLimit(),
    ReturnBefore(),
    AccessibilityRequired(),
    GroupCapacity(),
    TransportMode(),
)


class ConstraintEngine:
    """Evaluates every mandatory constraint and reports all outcomes."""

    def __init__(self, constraints: Sequence[Constraint] | None = None) -> None:
        self._constraints = tuple(constraints) if constraints is not None else DEFAULT_CONSTRAINTS

    def evaluate(
        self,
        request: SearchRequest,
        journey: Journey,
        destination: Destination,
        rules: Rules,
    ) -> FeasibilityReport:
        checks = [
            constraint.check(request, journey, destination, rules)
            for constraint in self._constraints
        ]
        return FeasibilityReport(feasible=all(check.satisfied for check in checks), checks=checks)
