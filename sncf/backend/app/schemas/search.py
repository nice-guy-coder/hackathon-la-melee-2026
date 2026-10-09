from __future__ import annotations

from datetime import date as Date
from datetime import time as Time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SearchRequest(BaseModel):
    """Search criteria provided by the frontend or extracted from a query."""

    model_config = ConfigDict(extra="forbid")

    origin: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
        description="Departure location",
    )

    max_budget_euros: float | None = Field(
        default=None,
        gt=0,
        le=100000,
        description="Maximum budget in euros per student",
    )

    max_travel_time_minutes: int | None = Field(
        default=None,
        gt=0,
        le=1440,
        description="Maximum travel time in minutes",
    )

    interests: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Teacher's preferred themes or interests",
    )

    accessibility: bool | None = Field(
        default=None,
        description="Whether accessible travel/destinations are required",
    )

    transport: str = Field(
        default="train",
        min_length=1,
        max_length=30,
        description="Preferred mode of transport",
    )

    students: int | None = Field(
        default=None,
        gt=0,
        le=2000,
        description="Number of students in the group",
    )

    date: Date | None = Field(
        default=None,
        description="Requested travel date",
    )

    return_before: Time | None = Field(
        default=None,
        description="Latest acceptable return time",
    )

    query: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional natural language request",
    )

    @field_validator("interests", mode="after")
    @classmethod
    def _clean_interests(cls, value: list[str]) -> list[str]:
        seen: list[str] = []
        for item in value:
            cleaned = item.strip()
            if cleaned and cleaned.casefold() not in {s.casefold() for s in seen}:
                seen.append(cleaned)
        return seen

    @field_validator("query", mode="before")
    @classmethod
    def _blank_query_is_none(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def _require_origin_or_query(self) -> "SearchRequest":
        if not self.origin and not self.query:
            raise ValueError("either 'origin' or 'query' must be provided")
        return self
