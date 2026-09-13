import pytest
from app.providers.events import normalize_ticketmaster
from app.providers.llm import ProviderError
from app.rag.index import LexicalEmbeddingProvider, LocalVectorIndex
from app.services.policies import generate_guide
from app.agents.tools import ToolRunner, immediate, EventsOutput


async def test_rag_venue_isolation_citations_and_persistence(config, events):
    path = config.data_dir / "knowledge/test-index.json"
    idx = LocalVectorIndex(config.data_dir / "knowledge/corpus.json", path)
    embed = LexicalEmbeddingProvider()
    await idx.ingest(embed)
    items = await idx.retrieve("bag policy outside food", embed, events[0], ["policy"])
    assert items and all(e.venue == "Excite Ballpark" for e in items)
    assert all(e.source_id and e.source_url.startswith("https://") and e.retrieval_score is not None for e in items)
    assert LocalVectorIndex(config.data_dir / "knowledge/corpus.json", path).ready(embed.model)
    guide = generate_guide(events[0], items)
    assert guide.policy.fields["bags"].source_id in {x.source_id for x in items}
    assert guide.policy.conflicts


async def test_irrelevant_context_and_embedding_mismatch(config, events):
    idx = LocalVectorIndex(config.data_dir / "knowledge/corpus.json", config.data_dir / "knowledge/test-index.json")
    embed = LexicalEmbeddingProvider()
    await idx.ingest(embed)
    assert await idx.retrieve("quantum superconducting qubit", embed, events[0], ["context"]) == []
    embed.model = "different-model"
    with pytest.raises(ProviderError):
        await idx.retrieve("bag", embed, events[0], ["policy"])


async def test_no_allergy_safe_fabrication(config, events):
    idx = LocalVectorIndex(config.data_dir / "knowledge/corpus.json", config.data_dir / "knowledge/test-index.json")
    embed = LexicalEmbeddingProvider()
    await idx.ingest(embed)
    evidence = await idx.retrieve("vegetarian food", embed, events[0], ["food"])
    guide = generate_guide(events[0], evidence)
    assert guide.food[0].vegetarian is None
    assert "not verified" in guide.food[0].allergen_information


async def test_tool_limits_and_timeout():
    import asyncio

    runner = ToolRunner(1, 0.01)
    result = await runner.run("search_events", lambda: asyncio.sleep(0.1))
    assert not result.ok and "time limit" in result.error
    result = await runner.run("search_events", lambda: immediate(EventsOutput(events=[])))
    assert not result.ok and "limit" in result.error
    assert runner.calls == 1


async def test_unknown_tool_is_rejected():
    runner = ToolRunner(10, 1)
    assert not (await runner.run("execute_shell", lambda: immediate(EventsOutput(events=[])))).ok
    assert runner.calls == 0


def tm_fixture():
    return {
        "id": "123",
        "name": "A vs B",
        "url": "https://www.ticketmaster.com/event/123",
        "dates": {"start": {"dateTime": "2026-10-10T19:00:00Z"}, "status": {"code": "onsale"}},
        "classifications": [{"segment": {"name": "Sports"}, "genre": {"name": "Baseball"}}],
        "_embedded": {
            "venues": [
                {
                    "name": "Oracle Park",
                    "city": {"name": "San Francisco"},
                    "state": {"stateCode": "CA"},
                    "location": {"latitude": "37.7786", "longitude": "-122.3893"},
                }
            ],
            "attractions": [{"name": "A"}, {"name": "B"}],
        },
        "priceRanges": [{"currency": "USD", "min": 30, "max": 90}],
    }


def test_ticketmaster_normalization():
    event = normalize_ticketmaster(tm_fixture())
    assert event.price_min == 30 and event.data_mode == "live"
    assert event.outing_extra is None and not event.signals
    assert event.coordinates.lat == 37.7786


@pytest.mark.parametrize("change", ["malformed", "cancelled", "tba", "currency"])
def test_provider_bad_input(change):
    raw = tm_fixture()
    if change == "malformed":
        raw = {}
    if change == "cancelled":
        raw["dates"]["status"]["code"] = "cancelled"
    if change == "tba":
        raw["dates"]["start"]["timeTBA"] = True
    if change == "currency":
        raw["priceRanges"][0]["currency"] = "EUR"
    event = normalize_ticketmaster(raw)
    assert event is None if change != "currency" else event.price_min is None
