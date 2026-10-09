from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search criteria provided by the frontend."""

    origin: str = Field(
        min_length=1,
        description="Departure location"
    )

    max_budget_euros: float | None = Field(
        default=None,
        gt=0,
        description="Maximum budget in euros"
    )

    max_travel_time_minutes: int | None = Field(
        default=None,
        gt=0,
        description="Maximum travel time in minutes"
    )

    interests: list[str] = Field(
        default_factory=list,
        description="Teacher's preferred themes or interests"
    )

    accessibility: bool | None = Field(
        default=None,
        description="Whether accessible travel/destinations are required"
    )

    transport: str = Field(
        default="train",
        min_length=1,
        description="Preferred mode of transport"
    )