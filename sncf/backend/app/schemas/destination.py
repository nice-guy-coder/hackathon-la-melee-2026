from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Destination(BaseModel):
    """An educational destination reachable by train."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=80)
    region: str = Field(default="Occitanie", max_length=80)
    themes: list[str] = Field(default_factory=list, max_length=20)
    accessible: bool = False
    description: str = Field(default="", max_length=500)
