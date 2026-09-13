from datetime import datetime, timedelta, timezone
import json
import httpx
import pytest
from app.models.domain import EventWeather
from app.providers.weather import WeatherProvider
from app.services.attire import attire_suggestions
from app.services.policies import generate_guide
from app.rag.index import LocalVectorIndex

NOW = datetime(2026, 9, 13, 1, tzinfo=timezone.utc)
START = NOW + timedelta(days=2, minutes=30)


def payload(start=START):
    hour = start.replace(minute=0)
    return {
        "hourly_units": {
            "time": "unixtime",
            "temperature_2m": "°F",
            "apparent_temperature": "°F",
            "precipitation_probability": "%",
            "wind_speed_10m": "mp/h",
        },
        "hourly": {
            "time": [int((hour + timedelta(hours=n)).timestamp()) for n in range(4)],
            "temperature_2m": [64, 61, 59, 58],
            "apparent_temperature": [61, 58, 55, 54],
            "precipitation_probability": [10, 35, 65, 50],
            "wind_speed_10m": [8, 12, 17, 15],
        },
    }


async def test_forecast_targets_venue_utc_window_and_caches_without_redating(events):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=payload())

    provider = WeatherProvider(transport=httpx.MockTransport(handle))
    event = events[0].model_copy(update={"start_time": START})
    weather = await provider.forecast(event, NOW)
    assert weather.status == "available"
    assert weather.feels_like_min_f == 54 and weather.rain_probability_max == 65
    assert weather.window_start == START.replace(minute=0)
    assert requests[0].url.params["latitude"] == str(event.coordinates.lat)
    assert requests[0].url.params["timezone"] == "UTC"
    assert requests[0].url.params["start_date"] == "2026-09-15"
    again = await provider.forecast(event, NOW + timedelta(minutes=20))
    assert again.retrieved_at == NOW and len(requests) == 1
    await provider.forecast(event, NOW + timedelta(minutes=31))
    assert len(requests) == 2


@pytest.mark.parametrize("offset", [-1, 17])
async def test_out_of_range_never_calls_weather_service(events, offset):
    def forbidden(request):
        raise AssertionError("Must not fetch a substitute day's forecast")

    event = events[0].model_copy(update={"start_time": NOW + timedelta(days=offset)})
    weather = await WeatherProvider(transport=httpx.MockTransport(forbidden)).forecast(event, NOW)
    assert weather.status == "outside_window" and weather.retrieved_at is None


@pytest.mark.parametrize("problem", ["http", "timeout", "missing_hour", "null_temp", "wrong_units", "nan", "malformed_units"])
async def test_bad_or_unavailable_forecasts_degrade_without_inventing_weather(events, problem):
    def handle(request):
        if problem == "timeout":
            raise httpx.ReadTimeout("offline")
        if problem == "http":
            return httpx.Response(429)
        data = payload()
        if problem == "missing_hour":
            data["hourly"]["time"].pop()
        if problem == "null_temp":
            data["hourly"]["temperature_2m"][0] = None
        if problem == "malformed_units":
            data["hourly_units"] = []
        if problem == "wrong_units":
            data["hourly_units"]["temperature_2m"] = "°C"
        if problem == "nan":
            # JSON may contain a non-standard numeric value; provider still rejects it.
            data["hourly"]["temperature_2m"][0] = float("nan")
            return httpx.Response(200, content=json.dumps(data).encode())
        return httpx.Response(200, json=data)

    event = events[0].model_copy(update={"start_time": START})
    weather = await WeatherProvider(transport=httpx.MockTransport(handle)).forecast(event, NOW)
    assert weather.status == "unavailable" and weather.temperature_min_f is None


async def test_null_rain_is_unknown_not_zero(events):
    data = payload()
    data["hourly"]["precipitation_probability"][1] = None
    event = events[0].model_copy(update={"start_time": START})
    weather = await WeatherProvider(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=data))).forecast(
        event, NOW
    )
    assert weather.status == "available" and weather.rain_probability_max is None
    assert "Rain probability is unavailable" in " ".join(attire_suggestions(weather, []))


def test_attire_uses_conditions_and_same_venue_rules(config, events):
    index = LocalVectorIndex(config.data_dir / "knowledge/corpus.json", config.data_dir / "absent.json")
    event = next(e for e in events if e.id == "bay-fc")
    weather = EventWeather(
        status="available", feels_like_min_f=45, feels_like_max_f=52, rain_probability_max=80, wind_max_mph=20
    )
    guide = generate_guide(event, index.visitor_evidence(event), weather)
    tips = " ".join(guide.attire_tips)
    assert "warm jacket" in tips and "rain jacket" in tips and "wind-resistant" in tips
    assert "restrict umbrella use" in tips and "prohibited" in guide.attire_rules[0].claim
    wrong = generate_guide(events[1], index.visitor_evidence(event), weather)
    assert not wrong.attire_rules and "restrict umbrella use" not in " ".join(wrong.attire_tips)
    hot = attire_suggestions(
        weather.model_copy(
            update={"feels_like_min_f": 82, "feels_like_max_f": 90, "rain_probability_max": 0, "wind_max_mph": 2}
        ),
        [],
    )
    assert "breathable" in " ".join(hot) and "rain jacket" not in " ".join(hot)


async def test_utc_window_covers_local_evening_across_midnight(events):
    start = datetime.fromisoformat("2026-09-15T16:30:00-07:00")
    utc = start.astimezone(timezone.utc)

    def handle(request):
        assert request.url.params["end_date"] == "2026-09-16"
        return httpx.Response(200, json=payload(utc))

    weather = await WeatherProvider(transport=httpx.MockTransport(handle)).forecast(
        events[0].model_copy(update={"start_time": start}), NOW
    )
    assert weather.status == "available" and weather.window_end.day == 16
