from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.destination import Destination
from app.schemas.journey import Journey
from app.schemas.rules import Rules


class DataSourceError(RuntimeError):
    """Raised when a data source cannot be loaded or queried."""


class JourneyRepository(ABC):
    """Port for retrieving round trip schedules."""

    @abstractmethod
    def list_journeys(self, origin: str | None = None) -> list[Journey]:
        raise NotImplementedError

    @abstractmethod
    def get_journey(self, journey_id: str) -> Journey | None:
        raise NotImplementedError


class DestinationRepository(ABC):
    """Port for retrieving destination metadata."""

    @abstractmethod
    def list_destinations(self) -> list[Destination]:
        raise NotImplementedError

    @abstractmethod
    def get_destination(self, destination_id: str) -> Destination | None:
        raise NotImplementedError


class RulesRepository(ABC):
    """Port for retrieving scoring and pricing rules."""

    @abstractmethod
    def get_rules(self) -> Rules:
        raise NotImplementedError


class DataLayer:
    """Bundle of repositories injected into the application service."""

    def __init__(
        self,
        journeys: JourneyRepository,
        destinations: DestinationRepository,
        rules: RulesRepository,
    ) -> None:
        self.journeys = journeys
        self.destinations = destinations
        self.rules = rules
