import json
import shutil
import pytest
from app.core.config import BACKEND, Settings
from app.models.domain import EventCandidate, UserIntent
from app.providers.distance import locate


@pytest.fixture
def events():
    return [EventCandidate.model_validate(x) for x in json.loads((BACKEND / "data/demo/events.json").read_text())]


@pytest.fixture
def family():
    return UserIntent(
        location="San Jose",
        coordinates=locate("San Jose"),
        radius_miles=25,
        budget=120,
        children=2,
        family_friendly=True,
        atmosphere="relaxed",
        dietary=["vegetarian"],
    )


@pytest.fixture
def config(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(BACKEND / "data/demo", data / "demo")
    shutil.copytree(BACKEND / "data/local_events", data / "local_events")
    (data / "knowledge").mkdir()
    shutil.copy(BACKEND / "data/knowledge/corpus.json", data / "knowledge/corpus.json")
    return Settings(data_dir=data, app_mode="fallback", weather_provider="disabled")
