"""Small, cached Open-Meteo adapter. Weather never changes event eligibility or rank."""

import asyncio
import math
from datetime import datetime, timedelta, timezone

import httpx

from app.models.domain import EventCandidate, EventWeather


class WeatherProvider:
    def __init__(self, enabled=True, transport=None):
        self.enabled, self.transport = enabled, transport
        self.cache: dict[tuple, tuple[datetime, EventWeather]] = {}

    async def forecast(self, event: EventCandidate, now: datetime | None = None) -> EventWeather:
        now = now or datetime.now(timezone.utc)
        if not self.enabled:
            return EventWeather(
                status="disabled", message="Weather lookup is disabled. Check the forecast before leaving."
            )
        start = event.start_time.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=3)
        if event.start_time < now:
            return EventWeather(
                status="outside_window",
                message="This event's start time has passed. An upcoming-event forecast is not available.",
            )
        if end.date() > now.astimezone(timezone.utc).date() + timedelta(days=15):
            return EventWeather(
                status="outside_window",
                message="This event is outside the available forecast window (up to 16 days). Check again closer to the date.",
            )
        key = (event.coordinates.lat, event.coordinates.lon, start.isoformat())
        cached = self.cache.get(key)
        if cached and now < cached[0]:
            return cached[1].model_copy(deep=True)
        params = dict(
            latitude=event.coordinates.lat,
            longitude=event.coordinates.lon,
            start_date=start.date().isoformat(),
            end_date=end.date().isoformat(),
            hourly="temperature_2m,apparent_temperature,precipitation_probability,wind_speed_10m",
            temperature_unit="fahrenheit",
            wind_speed_unit="mph",
            timezone="UTC",
            timeformat="unixtime",
        )
        try:
            # A total deadline bounds connect/read time and keeps the outing useful during outages.
            async with asyncio.timeout(6):
                async with httpx.AsyncClient(timeout=5, transport=self.transport) as client:
                    response = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
                    response.raise_for_status()
                    data = response.json()
            units = data["hourly_units"]
            if not isinstance(units, dict):
                raise ValueError("Invalid forecast metadata")
            if any(
                units.get(k) != v
                for k, v in {
                    "time": "unixtime",
                    "temperature_2m": "°F",
                    "apparent_temperature": "°F",
                    "precipitation_probability": "%",
                    "wind_speed_10m": "mp/h",
                }.items()
            ):
                raise ValueError("Unexpected forecast units")
            hourly = data["hourly"]
            times = hourly["time"]
            if not isinstance(times, list):
                raise ValueError("Invalid hourly timestamps")
            expected = [int((start + timedelta(hours=n)).timestamp()) for n in range(4)]
            if any(t not in times for t in expected):
                raise ValueError("Forecast does not cover the planning window")
            indices = [times.index(t) for t in expected]

            def values(name, low, high, optional=False):
                raw = [hourly[name][i] for i in indices]
                if optional and any(v is None for v in raw):
                    return None
                if any(
                    isinstance(v, bool)
                    or not isinstance(v, (int, float))
                    or not math.isfinite(v)
                    or not low <= v <= high
                    for v in raw
                ):
                    raise ValueError("Invalid weather observations")
                return raw

            temperatures = values("temperature_2m", -150, 150)
            feels = values("apparent_temperature", -180, 180)
            rain = values("precipitation_probability", 0, 100, optional=True)
            wind = values("wind_speed_10m", 0, 250)
            result = EventWeather(
                status="available",
                message="Outdoor forecast around the start time; the 3-hour planning window is not an estimate of event duration.",
                retrieved_at=now,
                window_start=start,
                window_end=end,
                temperature_min_f=min(temperatures),
                temperature_max_f=max(temperatures),
                feels_like_min_f=min(feels),
                feels_like_max_f=max(feels),
                rain_probability_max=max(rain) if rain is not None else None,
                wind_max_mph=max(wind),
            )
        except (httpx.HTTPError, TimeoutError, ValueError, KeyError, TypeError, IndexError):
            result = EventWeather()
        # Bound memory; never renew retrieval dates when returning cached data.
        self.cache = {k: v for k, v in self.cache.items() if now < v[0]}
        if len(self.cache) >= 128:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = (now + timedelta(minutes=30 if result.status == "available" else 1), result)
        return result.model_copy(deep=True)
