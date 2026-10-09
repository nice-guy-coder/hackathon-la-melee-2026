from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Pricing(BaseModel):
    """Group pricing rules applied on top of a base fare."""

    model_config = ConfigDict(extra="forbid")

    student_discount_pct: float = Field(default=0, ge=0, le=100)
    min_group_for_discount: int = Field(default=10, ge=1, le=2000)


class Rules(BaseModel):
    """Data-driven scoring and pricing configuration."""

    model_config = ConfigDict(extra="forbid")

    weights: dict[str, float] = Field(default_factory=dict)
    pricing: Pricing = Field(default_factory=Pricing)
    default_max_group_size: int = Field(default=80, ge=1, le=2000)

    @field_validator("weights", mode="after")
    @classmethod
    def _clamp_weights(cls, value: dict[str, float]) -> dict[str, float]:
        return {key: min(1.0, max(0.0, weight)) for key, weight in value.items()}

    def student_price(self, base_price: float, students: int | None) -> float:
        if students and students >= self.pricing.min_group_for_discount:
            discounted = base_price * (100 - self.pricing.student_discount_pct) / 100
            return round(discounted, 2)
        return base_price
