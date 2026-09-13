import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
import httpx
from pydantic import ValidationError
from app.core.config import Settings
from app.models.domain import Coordinates, EventCandidate, EvidenceItem, UserIntent
from app.providers.llm import ProviderError


class EventProvider(Protocol):
    async def search(self, intent: UserIntent) -> list[EventCandidate]: ...


class DemoEventProvider:
    def __init__(self, path: Path):
        self.path = path

    async def search(self, intent: UserIntent) -> list[EventCandidate]:
        return [EventCandidate.model_validate(e) for e in json.loads(self.path.read_text())]


class CuratedLocalEventProvider(DemoEventProvider):
    async def search(self, intent: UserIntent) -> list[EventCandidate]:
        return [e for e in await super().search(intent) if e.data_mode == "curated" and e.verification == "verified"]


def normalize_ticketmaster(raw: dict) -> EventCandidate | None:
    try:
        start = raw["dates"]["start"]
        if (
            start.get("dateTBD")
            or start.get("dateTBA")
            or start.get("timeTBA")
            or raw["dates"].get("status", {}).get("code") != "onsale"
        ):
            return None
        venue = raw["_embedded"]["venues"][0]
        classification = raw.get("classifications", [{}])[0]
        if classification.get("segment", {}).get("name") != "Sports":
            return None
        sport = classification.get("genre", {}).get("name", "unknown").lower()
        now = datetime.now(timezone.utc)
        price = next((p for p in raw.get("priceRanges", []) if p.get("currency") == "USD"), {})
        name = raw["name"]
        source = EvidenceItem(
            id=f"tm-{raw['id']}",
            claim=f"Ticketmaster lists {name} at {venue['name']}.",
            category="event",
            source_id=f"tm-{raw['id']}",
            source_title="Ticketmaster listing",
            source_url=raw["url"],
            authority="trusted",
            retrieved_at=now,
            confidence=0.85,
        )
        # No rivalry/atmosphere invented from event marketing. Curated enrichment must supply an attendance signal.
        return EventCandidate(
            id=f"tm-{raw['id']}",
            provider="ticketmaster",
            provider_event_id=raw["id"],
            name=name,
            sport=sport,
            league=classification.get("subGenre", {}).get("name", "Unknown"),
            level="professional",
            teams=[a["name"] for a in raw["_embedded"].get("attractions", [])],
            start_time=start["dateTime"],
            timezone=venue.get("timezone", "America/Los_Angeles"),
            venue=venue["name"],
            city=venue.get("city", {}).get("name", ""),
            state=venue.get("state", {}).get("stateCode", ""),
            coordinates=Coordinates(lat=venue["location"]["latitude"], lon=venue["location"]["longitude"]),
            price_min=price.get("min"),
            price_max=price.get("max"),
            price_basis="listed_range" if price else "unknown",
            ticket_url=raw["url"],
            source_url=raw["url"],
            retrieved_at=now,
            verification="verified",
            data_mode="live",
            evidence=[source],
            signals=[],
        )
    except (KeyError, IndexError, TypeError, ValueError, ValidationError):
        return None


class TicketmasterEventProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, intent: UserIntent) -> list[EventCandidate]:
        if not self.settings.ticketmaster_api_key:
            raise ProviderError("Ticketmaster credentials are not configured")
        params = {
            "apikey": self.settings.ticketmaster_api_key,
            "classificationName": "sports",
            "stateCode": "CA",
            "size": 100,
            "sort": "date,asc",
        }
        if intent.coordinates:
            params.update(
                latlong=f"{intent.coordinates.lat},{intent.coordinates.lon}",
                radius=intent.radius_miles or 100,
                unit="miles",
            )
        if intent.date_from:
            params["startDateTime"] = f"{intent.date_from}T00:00:00Z"
        if intent.date_to:
            params["endDateTime"] = f"{intent.date_to}T23:59:59Z"
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds) as client:
                    response = await client.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params)
                    response.raise_for_status()
                    raw = response.json().get("_embedded", {}).get("events", [])
                    return [e for r in raw if (e := normalize_ticketmaster(r)) is not None]
            except (httpx.HTTPError, ValueError):
                if attempt:
                    raise ProviderError("Ticketmaster could not return verified events") from None
                await asyncio.sleep(0.2)
        return []


def merge_events(live: list[EventCandidate], curated: list[EventCandidate]) -> list[EventCandidate]:
    result = {e.id: e for e in live}
    for event in curated:
        match = next(
            (
                e
                for e in result.values()
                if e.venue.casefold() == event.venue.casefold()
                and abs((e.start_time - event.start_time).total_seconds()) < 3600
                and bool(set(e.teams) & set(event.teams))
            ),
            None,
        )
        if match:
            result[match.id] = match.model_copy(
                update={
                    "signals": event.signals,
                    "significance": event.significance,
                    "experience": event.experience,
                    "family": event.family,
                    "level": event.level,
                    "evidence": match.evidence + event.evidence,
                }
            )
        else:
            result[event.id] = event
    return list(result.values())
