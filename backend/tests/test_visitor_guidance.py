from datetime import datetime, timedelta, timezone
import pytest
from app.models.domain import EvidenceItem, EventGuide, SearchRequest
from app.agents.orchestrator import Concierge
from app.rag.index import LocalVectorIndex
from app.services.policies import generate_guide


def fact(event, category, **changes):
    data = dict(
        id=category,
        claim="Venue-specific visitor instructions",
        category=category,
        source_id=category,
        source_title="Official guide",
        source_url=event.source_url,
        authority="venue_official",
        retrieved_at=datetime.now(timezone.utc),
        venue=event.venue,
        event_type=event.sport,
    )
    return EvidenceItem.model_validate({**data, **changes})


@pytest.mark.parametrize("category", ["parking", "seating", "food", "arrival"])
@pytest.mark.parametrize("scope", [{"venue": "Other venue"}, {"event_id": "other-event"}, {"event_type": "tennis"}])
def test_all_guide_details_reject_wrong_scope(events, category, scope):
    guide = generate_guide(events[0], [fact(events[0], category, **scope)])
    assert not getattr(guide, category)


def test_missing_and_stale_guidance_stays_honest(events):
    empty = generate_guide(events[0], [])
    assert not empty.parking and not empty.seating
    assert any("Parking details are not verified" in w for w in empty.warnings)
    assert empty.attire_tips and "forecast" in " ".join(empty.attire_tips)
    stale = generate_guide(events[0], [fact(events[0], "parking", freshness="stale")])
    assert stale.parking[0].freshness == "stale"
    assert any("older source" in w for w in stale.warnings)
    # Historical stored responses can still deserialize after the API extension.
    old = EventGuide.model_validate({"policy": empty.policy.model_dump()})
    assert old.parking == [] and old.attire_tips == []


def test_every_demo_venue_has_scoped_guidance(config, events):
    index = LocalVectorIndex(config.data_dir / "knowledge/corpus.json", config.data_dir / "absent.json")
    for event in events:
        facts = index.visitor_evidence(event)
        assert {e.category for e in facts} >= {"parking", "seating"}
        assert all(e.venue == event.venue and e.event_type == event.sport for e in facts)
        wrong_sport = event.model_copy(update={"sport": "tennis"})
        assert index.visitor_evidence(wrong_sport) == []
    sj = next(e for e in index.visitor_evidence(events[0]) if e.category == "parking")
    assert sj.freshness == "stale"  # 2025 instructions remain old despite this week's review.
    document = next(d for d in index.chunks if d["category"] == "seating")
    old = {**document, "ingestion_date": (datetime.now(timezone.utc) - timedelta(days=91)).isoformat()}
    assert index.evidence(old, 1).freshness == "stale"


async def test_guide_enrichment_is_cited_and_does_not_change_rank(config):
    service = Concierge(config)
    result = await service.recommend(SearchRequest(query="Family outing", preset="family", mode="fallback"))
    assert result.recommendations[0].event.id == "sj-giants"
    for recommendation in result.recommendations:
        assert recommendation.guide.parking and recommendation.guide.seating
        ids = {e.id for e in recommendation.citations}
        assert all(e.id in ids for e in recommendation.guide.parking + recommendation.guide.seating)
    assert result.provider_status["tool_calls"] <= 10
