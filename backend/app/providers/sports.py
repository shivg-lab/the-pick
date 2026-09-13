import re
from datetime import datetime, timezone
from typing import Protocol
import httpx
from app.core.config import Settings
from app.models.domain import EventCandidate, EvidenceItem
from app.providers.llm import ProviderError


class SportsProvider(Protocol):
    async def get(self, events: list[EventCandidate]) -> dict[str, list[EvidenceItem]]: ...


class DemoSportsProvider:
    async def get(self, events: list[EventCandidate]) -> dict[str, list[EvidenceItem]]:
        # Fixture rubric is explicit; no invented standings, records or live scores.
        return {e.id: e.evidence for e in events}


class SportradarSportsProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def get(self, events: list[EventCandidate]) -> dict[str, list[EvidenceItem]]:
        path = self.settings.sportradar_feed_path
        if not self.settings.sportradar_api_key or not re.fullmatch(r"[a-zA-Z0-9_/-]+\.json", path) or ".." in path:
            raise ProviderError("Sportradar credentials or licensed schedule feed are not configured")
        try:
            async with httpx.AsyncClient(timeout=self.settings.provider_timeout_seconds) as client:
                response = await client.get(
                    f"https://api.sportradar.com/{path}", headers={"x-api-key": self.settings.sportradar_api_key}
                )
                response.raise_for_status()
                games = response.json().get("games", [])
            result = {e.id: [] for e in events}
            for e in events:
                for g in games:
                    home, away = g.get("home", {}).get("name"), g.get("away", {}).get("name")
                    if {home, away} != set(e.teams) or not g.get("scheduled"):
                        continue
                    scheduled = datetime.fromisoformat(g["scheduled"].replace("Z", "+00:00"))
                    if abs((scheduled - e.start_time).total_seconds()) > 3600:
                        continue
                    result[e.id].append(
                        EvidenceItem(
                            id=f"sr-{g['id']}",
                            claim=f"Sportradar schedule confirms {home} vs. {away} at {scheduled.isoformat()}.",
                            category="sports",
                            source_id=f"sr-{g['id']}",
                            source_title="Sportradar licensed schedule",
                            source_url=f"https://api.sportradar.com/{path}",
                            authority="trusted",
                            retrieved_at=datetime.now(timezone.utc),
                            confidence=0.9,
                        )
                    )
            return result
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            raise ProviderError("Sportradar could not provide matching sports evidence") from None
