from __future__ import annotations

import json
import logging
import re
from datetime import date as Date
from datetime import time as Time
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.schemas.recommendation import TrustLevel

logger = logging.getLogger(__name__)

_ALLOWED_FIELDS = (
    "origin",
    "max_budget_euros",
    "max_travel_time_minutes",
    "interests",
    "accessibility",
    "transport",
    "students",
    "date",
    "return_before",
)


class ExtractedConstraints(BaseModel):
    """Validated subset of search constraints extracted from free text."""

    model_config = ConfigDict(extra="forbid")

    origin: str | None = Field(default=None, min_length=1, max_length=80)
    max_budget_euros: float | None = Field(default=None, gt=0, le=100000)
    max_travel_time_minutes: int | None = Field(default=None, gt=0, le=1440)
    interests: list[str] | None = Field(default=None, max_length=20)
    accessibility: bool | None = None
    transport: str | None = Field(default=None, min_length=1, max_length=30)
    students: int | None = Field(default=None, gt=0, le=2000)
    date: Date | None = None
    return_before: Time | None = None


class ParsedQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    values: dict[str, Any] = Field(default_factory=dict)
    fields: list[str] = Field(default_factory=list)
    parser: str = Field(min_length=1, max_length=40)
    trust: TrustLevel


class RequestParser(Protocol):
    name: str

    def parse(self, query: str) -> ParsedQuery:
        ...


def _to_parsed(constraints: ExtractedConstraints, parser: str, trust: TrustLevel) -> ParsedQuery:
    values = constraints.model_dump(exclude_none=True)
    if values.get("interests") == []:
        values.pop("interests", None)
    return ParsedQuery(
        values=values,
        fields=[field for field in _ALLOWED_FIELDS if field in values],
        parser=parser,
        trust=trust,
    )


_ORIGIN = re.compile(
    r"(?:depuis|au d[ée]part de|d[ée]part de|partant de|from|departing from)\s+"
    r"([\w\u00c0-\u017f'\u2019\-]+(?:\s+[\w\u00c0-\u017f'\u2019\-]+){0,2})",
    re.IGNORECASE,
)
_ORIGIN_STOPWORDS = {
    "avec", "pour", "moins", "et", "within", "under", "less", "with",
    "le", "la", "les", "de", "du", "the", "in", "on", "au", "aux",
}
_STUDENTS = re.compile(
    r"(\d{1,4})\s*(?:[ée]l[èe]ves?|eleves?|students?|pupils?|children|kids?|enfants)",
    re.IGNORECASE,
)
_DURATION_HOURS = re.compile(
    r"(?:moins de|under|less than|max(?:imum)?|no more than|dans les)\s*"
    r"(\d{1,3})\s*h(?:eures?)?(?:\s*(\d{1,2}))?",
    re.IGNORECASE,
)
_DURATION_MINUTES = re.compile(
    r"(?:moins de|under|less than|max(?:imum)?|no more than|dans les)\s*"
    r"(\d{1,4})\s*(?:min(?:utes?)?)",
    re.IGNORECASE,
)
_RETURN_BEFORE = re.compile(
    r"(?:retour\s+avant|de\s+retour\s+avant|back\s+before|return\s+before|avant)\s+"
    r"(\d{1,2})\s*[h:]\s*(\d{2})?",
    re.IGNORECASE,
)
_BUDGET = re.compile(
    r"(?:moins de|under|less than|budget(?:\s+de)?|max(?:imum)?(?:\s+de)?)\s*"
    r"(\d{1,5})\s*(?:\u20ac|euros?|eur)\b",
    re.IGNORECASE,
)
_ACCESSIBLE = re.compile(
    r"\b(pmr|accessible|accessibilit[ée]|handicap[ée]?s?|mobilit[ée]\s+r[ée]duite|mpr)\b",
    re.IGNORECASE,
)
_DATE_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_DATE_FR = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_THEMES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("science", re.compile(r"scienti\w*|science|espace|space|astronom\w*", re.IGNORECASE)),
    ("nature", re.compile(r"nature|naturelle?|animaux|faune|flore|forest|for[êe]t", re.IGNORECASE)),
    ("history", re.compile(r"histoire|historique|history|patrimoine|m[ée]di[ée]val|ch[âa]teau|castle", re.IGNORECASE)),
    ("culture", re.compile(r"culture\w*|mus[ée]e?|museum|cin[ée]ma", re.IGNORECASE)),
    ("arts", re.compile(r"\barts?\b|artistique", re.IGNORECASE)),
    ("sport", re.compile(r"sport\w*|randonn[ée]e|plein air", re.IGNORECASE)),
)


class HeuristicParser:
    """Deterministic rule-based extraction used when no LLM is available."""

    name = "heuristic"

    def parse(self, query: str) -> ParsedQuery:
        values: dict[str, Any] = {}

        origin = self._origin(query)
        if origin:
            values["origin"] = origin

        students = _first_int(_STUDENTS.search(query))
        if students is not None:
            values["students"] = students

        duration = self._duration(query)
        if duration is not None:
            values["max_travel_time_minutes"] = duration

        return_before = self._return_before(query)
        if return_before is not None:
            values["return_before"] = return_before

        budget = _first_int(_BUDGET.search(query))
        if budget is not None:
            values["max_budget_euros"] = float(budget)

        if _ACCESSIBLE.search(query):
            values["accessibility"] = True

        interests = [theme for theme, pattern in _THEMES if pattern.search(query)]
        if interests:
            values["interests"] = interests

        parsed_date = self._date(query)
        if parsed_date is not None:
            values["date"] = parsed_date

        try:
            constraints = ExtractedConstraints(**values)
        except ValidationError:
            logger.warning("Heuristic extraction produced invalid values; ignoring them.")
            constraints = ExtractedConstraints()
        return _to_parsed(constraints, self.name, TrustLevel.CALCULATED)

    @staticmethod
    def _origin(query: str) -> str | None:
        match = _ORIGIN.search(query)
        if not match:
            return None
        collected: list[str] = []
        for token in match.group(1).split():
            if token.casefold() in _ORIGIN_STOPWORDS or any(char.isdigit() for char in token):
                break
            collected.append(token)
        if not collected:
            return None
        return " ".join(collected)

    @staticmethod
    def _duration(query: str) -> int | None:
        hours = _DURATION_HOURS.search(query)
        if hours:
            total = int(hours.group(1)) * 60
            if hours.group(2):
                total += int(hours.group(2))
            return total
        minutes = _DURATION_MINUTES.search(query)
        if minutes:
            return int(minutes.group(1))
        return None

    @staticmethod
    def _return_before(query: str) -> Time | None:
        match = _RETURN_BEFORE.search(query)
        if not match:
            return None
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        if hour > 23 or minute > 59:
            return None
        return Time(hour=hour, minute=minute)

    @staticmethod
    def _date(query: str) -> Date | None:
        iso = _DATE_ISO.search(query)
        if iso:
            try:
                return Date.fromisoformat(iso.group(1))
            except ValueError:
                return None
        french = _DATE_FR.search(query)
        if french:
            try:
                return Date(int(french.group(3)), int(french.group(2)), int(french.group(1)))
            except ValueError:
                return None
        return None


def _first_int(match: re.Match[str] | None) -> int | None:
    if not match:
        return None
    return int(match.group(1))


_SYSTEM_PROMPT = (
    "You extract school trip search constraints from a teacher request. "
    "Reply with a single JSON object and nothing else. Allowed keys: "
    "origin (string), students (integer), date (YYYY-MM-DD), return_before (HH:MM), "
    "max_budget_euros (number), max_travel_time_minutes (integer), "
    "interests (array of lowercase theme strings), accessibility (boolean), transport (string). "
    "Omit unknown keys. Never guess whether a trip is feasible."
)


class OllamaParser:
    """Server-side LLM extraction that always falls back to heuristic parsing."""

    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_seconds: float = 15.0,
        fallback: RequestParser | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._fallback = fallback or HeuristicParser()

    def parse(self, query: str) -> ParsedQuery:
        try:
            raw = self._complete(query)
            constraints = ExtractedConstraints(**self._filter_keys(self._decode(raw)))
            return _to_parsed(constraints, self.name, TrustLevel.AI_ASSISTED)
        except Exception:
            logger.exception("LLM extraction failed; falling back to heuristic parsing.")
            return self._fallback.parse(query)

    def _complete(self, query: str) -> str:
        import httpx

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
        }
        response = httpx.post(
            f"{self._base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    @staticmethod
    def _decode(raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("LLM response did not contain a JSON object.")
        return json.loads(cleaned[start : end + 1])

    @staticmethod
    def _filter_keys(data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("LLM response was not a JSON object.")
        return {key: value for key, value in data.items() if key in _ALLOWED_FIELDS}


def create_parser(settings: Any) -> RequestParser:
    if not settings.llm_enabled:
        return HeuristicParser()
    return OllamaParser(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
        fallback=HeuristicParser(),
    )
