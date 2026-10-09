from __future__ import annotations

from datetime import date as Date
from datetime import time as Time

from pydantic import BaseModel, ConfigDict, Field


class Journey(BaseModel):
    """A round trip schedule served by a transport provider."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=60)
    origin: str = Field(min_length=1, max_length=80)
    destination_id: str = Field(min_length=1, max_length=40)
    date: Date
    departure_time: Time
    return_time: Time
    duration_minutes: int = Field(gt=0, le=1440)
    price_euros: float = Field(gt=0, le=100000)
    reliability_pct: float = Field(ge=0, le=100)
    group_capacity: int = Field(ge=0, le=2000)
    accessible: bool = False
    transport: str = Field(default="train", min_length=1, max_length=30)
    operator: str = Field(default="SNCF", max_length=80)
