import asyncio
from typing import Awaitable, Callable, Generic, Literal, TypeVar
from pydantic import BaseModel, Field
from app.models.domain import EventCandidate, EvidenceItem, StrictModel, UserIntent
from app.providers.llm import ProviderError


class ToolInput(StrictModel):
    event_ids: list[str] = Field(default_factory=list, max_length=10)
    query: str = Field(default="", max_length=500)


class ToolCall(StrictModel):
    name: Literal["get_sports_data", "retrieve_sports_context", "retrieve_venue_policy", "retrieve_food_options"]
    arguments: ToolInput


class ToolPlan(StrictModel):
    calls: list[ToolCall] = Field(default_factory=list, max_length=4)
    sufficient: bool = False


class EvidenceOutput(StrictModel):
    evidence: dict[str, list[EvidenceItem]]


class EventsOutput(StrictModel):
    events: list[EventCandidate]


class QualificationInput(StrictModel):
    events: list[EventCandidate]
    intent: UserIntent
    allow_illustrative: bool = True


class QualificationOutput(StrictModel):
    events: list[EventCandidate]
    exclusions: list[dict[str, str]]


class DistanceOutput(StrictModel):
    distances: dict[str, float | None]


T = TypeVar("T", bound=BaseModel)


class ToolResult(BaseModel, Generic[T]):
    name: str
    ok: bool
    data: T | None = None
    error: str | None = None
    source_ids: list[str] = Field(default_factory=list)


TOOL_DESCRIPTIONS = {
    "parse_user_request": "Parse and validate user intent using Ollama JSON Schema.",
    "search_events": "Read event inventory; event APIs establish schedules and prices.",
    "qualify_events": "Enforce public spectator eligibility, dates, distance, sport, team and budget.",
    "calculate_distance": "Calculate straight-line miles, never travel time.",
    "get_sports_data": "Check supplied sports provider; demo has fixture assumptions, not live standings.",
    "retrieve_sports_context": "Retrieve rivalry, history, traditions and atmosphere from the local vector index.",
    "retrieve_venue_policy": "Retrieve bag, food, water, re-entry, arrival and accessibility evidence for selected venues.",
    "retrieve_food_options": "Retrieve dietary options and missing-menu evidence for selected venues.",
    "score_and_rank_events": "Apply fixed deterministic score and separate confidence; model cannot change scores.",
    "generate_event_guide": "Resolve policies, look up exact-venue parking and seating sources, and assemble visitor guidance with separate comfort suggestions.",
}


class ToolRunner:
    def __init__(self, max_calls: int, timeout: float):
        self.max_calls, self.timeout, self.calls = max_calls, timeout, 0
        self.history: list[ToolResult] = []

    async def run(self, name: str, operation: Callable[[], Awaitable[T]]) -> ToolResult[T]:
        if name not in TOOL_DESCRIPTIONS:
            return ToolResult(name=name, ok=False, error="Unknown tool")
        if self.calls >= self.max_calls:
            return ToolResult(name=name, ok=False, error="Tool call limit reached")
        self.calls += 1
        try:
            data = await asyncio.wait_for(operation(), timeout=self.timeout)
            source_ids = []
            if isinstance(data, EvidenceOutput):
                source_ids = sorted({e.source_id for items in data.evidence.values() for e in items})
            if isinstance(data, EventsOutput):
                source_ids = sorted({e.source_id for event in data.events for e in event.evidence})
            result = ToolResult(name=name, ok=True, data=data, source_ids=source_ids)
        except asyncio.TimeoutError:
            result = ToolResult(name=name, ok=False, error=f"{name} exceeded its time limit")
        except ProviderError as exc:
            result = ToolResult(name=name, ok=False, error=f"{name}: {exc}")
        except (ValueError, OSError):
            result = ToolResult(name=name, ok=False, error=f"{name} could not return validated evidence")
        self.history.append(result)
        return result


async def immediate(value: T) -> T:
    return value
