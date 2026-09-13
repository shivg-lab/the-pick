from datetime import date, datetime
from typing import Any, Literal
from urllib.parse import urlparse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Coordinates(StrictModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class UserIntent(StrictModel):
    raw_query: str = Field(default="", max_length=2000)
    location: str = Field(default="San Jose", max_length=120)
    coordinates: Coordinates | None = None
    date_from: date | None = None
    date_to: date | None = None
    radius_miles: float | None = Field(default=None, gt=0, le=500)
    sports: list[str] = Field(default_factory=list, max_length=10)
    teams: list[str] = Field(default_factory=list, max_length=10)
    budget: float | None = Field(default=None, ge=0, le=100000)
    budget_type: Literal["total", "per_ticket"] = "total"
    adults: int = Field(default=2, ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)
    family_friendly: bool = False
    atmosphere: Literal["any", "relaxed", "electric", "iconic", "rivalry"] = "any"
    local_openness: bool = True
    dietary: list[str] = Field(default_factory=list, max_length=10)
    dietary_required: bool = False
    accessibility: list[str] = Field(default_factory=list, max_length=10)
    first_time: bool = False
    additional_constraints: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def ordered_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("End date must be on or after start date")
        if any(
            len(s) > 200
            for xs in [self.sports, self.teams, self.dietary, self.accessibility, self.additional_constraints]
            for s in xs
        ):
            raise ValueError("Preference is too long")
        return self


class SearchRequest(StrictModel):
    query: str = Field(min_length=3, max_length=2000)
    filters: dict[str, Any] = Field(default_factory=dict)
    preset: Literal["family", "iconic"] | None = None
    mode: Literal["auto", "agent", "fallback"] = "auto"

    @field_validator("filters")
    @classmethod
    def valid_filters(cls, v):
        UserIntent.model_validate(v)
        return v


class EvidenceItem(StrictModel):
    id: str
    claim: str
    category: str
    source_id: str
    source_title: str
    source_url: str
    authority: Literal["event_official", "team_official", "venue_official", "official", "trusted", "illustrative"]
    retrieved_at: datetime
    effective_date: date | None = None
    freshness: Literal["current", "stale", "historical", "illustrative"] = "current"
    confidence: float = Field(default=0.9, ge=0, le=1)
    retrieval_score: float | None = None
    venue: str | None = None
    event_id: str | None = None
    event_type: str | None = None
    field: str | None = None
    value: Any = None

    @field_validator("source_url")
    @classmethod
    def safe_url(cls, v):
        if v.startswith("/api/"):
            return v
        u = urlparse(v)
        if u.scheme != "https" or not u.hostname or u.username:
            raise ValueError("Source must be an HTTPS URL")
        return v


class EventCandidate(StrictModel):
    id: str
    provider: str
    provider_event_id: str
    name: str
    sport: str
    league: str
    level: Literal["professional", "local", "college"]
    teams: list[str]
    start_time: datetime
    timezone: str = "America/Los_Angeles"
    venue: str
    city: str
    state: str = "CA"
    coordinates: Coordinates
    price_min: float | None = Field(default=None, ge=0)
    price_max: float | None = Field(default=None, ge=0)
    price_basis: Literal["illustrative", "listed_range", "unknown"] = "unknown"
    outing_extra: float | None = Field(default=None, ge=0)
    ticket_url: str
    source_url: str
    image: str | None = None
    retrieved_at: datetime
    verification: Literal["verified", "illustrative", "unverified", "outdated"]
    data_mode: Literal["live", "curated", "illustrative"]
    public_access: bool = True
    spectator_event: bool = True
    date_confirmed: bool = True
    venue_confirmed: bool = True
    signals: list[str] = Field(default_factory=list)
    # Editorial inputs are explicitly labeled fixture assumptions, never live statistics.
    significance: float | None = Field(default=None, ge=0, le=100)
    experience: float | None = Field(default=None, ge=0, le=100)
    family: float | None = Field(default=None, ge=0, le=100)
    atmosphere: str = "electric"
    color: str = "orange"
    evidence: list[EvidenceItem] = Field(default_factory=list)

    @field_validator("start_time", "retrieved_at")
    @classmethod
    def timezone_required(cls, v):
        if v.tzinfo is None:
            raise ValueError("Timestamp must include a timezone")
        return v

    @field_validator("ticket_url", "source_url")
    @classmethod
    def safe_url(cls, v):
        return EvidenceItem.safe_url(v)

    @model_validator(mode="after")
    def ordered_price(self):
        if self.price_min is not None and self.price_max is not None and self.price_max < self.price_min:
            raise ValueError("Invalid price range")
        return self


class VenuePolicy(StrictModel):
    venue: str
    fields: dict[str, EvidenceItem] = Field(default_factory=dict)
    conflicts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    last_verified: date | None = None


class FoodOption(StrictModel):
    venue: str
    vendor: str
    location: str | None = None
    cuisine: str = "Concessions"
    vegetarian: bool | None = None
    vegan: bool | None = None
    gluten_free: bool | None = None
    allergen_information: str = "Allergen suitability and cross-contact are not verified. Ask the venue."
    evidence: EvidenceItem


class ScoreBreakdown(StrictModel):
    factors: dict[str, float | None]
    weights: dict[str, float]
    opportunity_score: float
    evidence_confidence: int
    missing_factors: list[str]
    rationale: dict[str, str]


class EventWeather(StrictModel):
    status: Literal["available", "outside_window", "unavailable", "disabled"] = "unavailable"
    message: str = "Weather could not be checked. Try a new search later."
    source_url: str = "https://open-meteo.com/"
    retrieved_at: datetime | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None
    temperature_min_f: float | None = None
    temperature_max_f: float | None = None
    feels_like_min_f: float | None = None
    feels_like_max_f: float | None = None
    rain_probability_max: float | None = None
    wind_max_mph: float | None = None


class EventGuide(StrictModel):
    policy: VenuePolicy
    food: list[FoodOption] = Field(default_factory=list)
    arrival: list[str] = Field(default_factory=list)
    parking: list[EvidenceItem] = Field(default_factory=list)
    seating: list[EvidenceItem] = Field(default_factory=list)
    attire_tips: list[str] = Field(default_factory=list)
    attire_rules: list[EvidenceItem] = Field(default_factory=list)
    weather: EventWeather = Field(default_factory=EventWeather)
    seating_tip: str = ""
    warnings: list[str] = Field(default_factory=list)


class Recommendation(StrictModel):
    event: EventCandidate
    rank: int
    score: ScoreBreakdown
    distance_miles: float | None
    estimated_total: float | None
    explanation: str
    why_it_matters: list[str]
    why_it_fits: list[str]
    tradeoffs: list[str]
    guide: EventGuide
    citations: list[EvidenceItem]
    warnings: list[str]
    data_mode: str


class Activity(StrictModel):
    step: str
    status: Literal["complete", "warning"] = "complete"
    tool: str | None = None
    source_ids: list[str] = Field(default_factory=list)


class RecommendationResponse(StrictModel):
    request_id: str
    parsed_intent: UserIntent
    candidates_considered: int
    exclusions: list[dict[str, str]]
    recommendations: list[Recommendation]
    baseline: list[dict[str, Any]]
    activity: list[Activity]
    data_mode: str
    agent_active: bool
    retrieval_mode: str
    provider_status: dict[str, Any]
    warnings: list[str]
    processing_ms: int
    created_at: datetime


class Feedback(StrictModel):
    request_id: str = Field(min_length=1, max_length=64)
    event_id: str = Field(min_length=1, max_length=128)
    rating: Literal["up", "down"] | None = None
    would_attend: bool | None = None
    reason: str = Field(default="", max_length=1000)
    correction: str = Field(default="", max_length=1000)
