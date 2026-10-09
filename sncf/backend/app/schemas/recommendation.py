from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.search import SearchRequest


class TrustLevel(str, Enum):
    VERIFIED = "VERIFIED"
    CALCULATED = "CALCULATED"
    AI_ASSISTED = "AI-ASSISTED"


class Reason(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=120)
    detail: str = Field(min_length=1, max_length=500)
    trust: TrustLevel


class CheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str = Field(min_length=1, max_length=80)
    satisfied: bool
    message: str = Field(min_length=1, max_length=500)
    trust: TrustLevel


class ScoreComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor: str = Field(min_length=1, max_length=80)
    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)
    weighted_score: float = Field(ge=0, le=100)
    trust: TrustLevel


class ConfidenceComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor: str = Field(min_length=1, max_length=80)
    value: float = Field(ge=0, le=100)
    trust: TrustLevel


class ConfidenceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall: float = Field(ge=0, le=100)
    components: list[ConfidenceComponent] = Field(default_factory=list)


class FeasibilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feasible: bool
    checks: list[CheckResult] = Field(default_factory=list)

    @property
    def failed(self) -> list[CheckResult]:
        return [check for check in self.checks if not check.satisfied]

    @property
    def passed(self) -> list[CheckResult]:
        return [check for check in self.checks if check.satisfied]


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    journey: Journey
    destination: Destination
    feasible: bool
    trip_score: float = Field(ge=0, le=100)
    confidence: ConfidenceReport
    breakdown: list[ScoreComponent] = Field(default_factory=list)
    reasons: list[Reason] = Field(default_factory=list)
    violations: list[CheckResult] = Field(default_factory=list)


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: SearchRequest
    extractor: str = Field(default="form", max_length=40)
    ai_assisted: bool = False
    data_source: str = Field(max_length=40)
    feasible_count: int = Field(ge=0)
    rejected_count: int = Field(ge=0)
    recommendations: list[Recommendation] = Field(default_factory=list)


class CompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: SearchRequest
    journey_ids: list[str] = Field(min_length=2, max_length=5)


class CompareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results: list[Recommendation] = Field(default_factory=list)
