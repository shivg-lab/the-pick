from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from app.models.domain import Coordinates, EvidenceItem, SearchRequest, UserIntent
from app.providers.distance import HaversineDistanceProvider, locate
from app.ranking.engine import eligibility, hard_filters, estimated_total, need_filters, rank, score
from app.services.policies import CONFLICT, resolve_policies


def evidence(id="a", **kwargs):
    return EvidenceItem(
        id=id,
        claim="Clear bags only",
        source_id=id,
        source_title="Official policy",
        source_url="https://www.milb.com/san-jose/ballpark/a-z-guide",
        category="policy",
        authority="venue_official",
        retrieved_at=datetime.now(timezone.utc),
        venue="Excite Ballpark",
        field="bags",
        **kwargs,
    )


@pytest.mark.parametrize(
    "change",
    [
        {"public_access": False},
        {"spectator_event": False},
        {"date_confirmed": False},
        {"venue_confirmed": False},
        {"signals": []},
        {"verification": "unverified"},
        {"evidence": []},
    ],
)
def test_eligibility_exclusions(events, change):
    assert eligibility(events[0].model_copy(update=change))


def test_illustrative_never_enters_hybrid(events):
    assert not eligibility(events[0])
    assert eligibility(events[0], False)


def test_past_live_event_rejected(events):
    event = events[0].model_copy(
        update={
            "start_time": datetime.now(timezone.utc) - timedelta(days=1),
            "data_mode": "curated",
            "verification": "verified",
        }
    )
    assert "already occurred" in " ".join(eligibility(event))


def test_distance():
    p = HaversineDistanceProvider()
    assert p.miles(locate("San Jose"), locate("San Jose")) == 0
    assert 40 < p.miles(locate("San Jose"), locate("San Francisco")) < 45
    assert locate("99999") is None


def test_total_budget_counts_all_people_and_extras(events, family):
    assert estimated_total(events[0], family) == 92
    assert not hard_filters(events[0], family)
    assert "Over your budget" in hard_filters(events[2], family)


def test_missing_price_and_extra_fail_budget(events, family):
    for change in ({"price_min": None}, {"outing_extra": None}):
        assert hard_filters(events[0].model_copy(update=change), family)


def test_per_ticket_budget(events, family):
    assert not hard_filters(events[0], family.model_copy(update={"budget_type": "per_ticket", "budget": 14}))
    assert hard_filters(events[0], family.model_copy(update={"budget_type": "per_ticket", "budget": 13}))


def test_hard_filters(events, family):
    for change in (
        {"sports": ["soccer"]},
        {"teams": ["49ers"]},
        {"radius_miles": 0.01},
        {"local_openness": False},
        {"date_from": datetime(2027, 1, 1).date()},
        {"coordinates": None},
    ):
        assert hard_filters(events[0], family.model_copy(update=change))


def test_date_is_venue_local(events):
    intent = UserIntent(date_from="2026-09-19", date_to="2026-09-19")
    assert not hard_filters(events[0], intent)
    assert hard_filters(events[2], intent)


def test_scoring_is_deterministic_and_reweights(events, family):
    a = score(events[0], family, [])
    b = score(events[0], family, [])
    assert a == b
    assert abs(sum(a.weights.values()) - 1) < 0.00001
    assert a.factors["personal_needs"] is None
    assert a.weights["personal_needs"] == 0
    assert a.evidence_confidence <= 75


def test_no_hidden_gem_bonus(events, family):
    assert score(events[0], family, []) == score(events[0].model_copy(update={"level": "professional"}), family, [])


def test_unavailable_factor_does_not_become_neutral(events):
    s = score(events[0].model_copy(update={"significance": None}), UserIntent(), [])
    assert s.factors["significance"] is None
    assert s.weights["significance"] == 0


def test_rank_stable_across_input_order(events, family):
    eligible = [e for e in events if not hard_filters(e, family)]
    assert [e.id for e, s in rank(eligible, family, {})] == [
        e.id for e, s in rank(list(reversed(eligible)), family, {})
    ]


def test_contrasting_presets_are_not_fixed_winners(events, family):
    local = [e for e in events if not hard_filters(e, family)]
    iconic = UserIntent(atmosphere="iconic")
    assert rank(local, family, {})[0][0].id == "sj-giants"
    assert rank(events, iconic, {})[0][0].id == "big-game"
    assert (
        rank(local, family.model_copy(update={"atmosphere": "rivalry", "children": 0, "family_friendly": False}), {})[
            0
        ][0].id
        != "sj-giants"
    )


def test_confidence_drops_for_stale_and_missing_evidence(events, family):
    source = evidence()
    good = score(events[0], family, [source])
    stale = score(events[0], family, [source.model_copy(update={"freshness": "stale"})])
    assert stale.evidence_confidence < good.evidence_confidence
    assert score(events[0], family, []).evidence_confidence < good.evidence_confidence


def test_required_diet_and_accessibility_need_evidence():
    assert need_filters(UserIntent(dietary=["vegan"], dietary_required=True), [])
    assert need_filters(UserIntent(accessibility=["wheelchair"]), [])
    assert not need_filters(UserIntent(dietary=["vegan"], dietary_required=False), [])


def test_policy_precedence_and_conflicts(events):
    general = evidence()
    specific = general.model_copy(
        update={
            "id": "b",
            "source_id": "b",
            "claim": "No bags at this event",
            "authority": "event_official",
            "event_id": events[0].id,
        }
    )
    p = resolve_policies(events[0], [general, specific])
    assert p.fields["bags"].id == "b"
    assert CONFLICT in p.conflicts


def test_wrong_event_policy_cannot_override(events):
    wrong = evidence().model_copy(update={"authority": "event_official", "event_id": "other"})
    assert not resolve_policies(events[0], [wrong]).fields


def test_stale_policy_warns(events):
    p = resolve_policies(events[0], [evidence().model_copy(update={"freshness": "stale"})])
    assert any("older than" in w for w in p.warnings)


@pytest.mark.parametrize(
    "data",
    [
        {"adults": 0},
        {"children": -1},
        {"budget": -1},
        {"radius_miles": 0},
        {"date_from": "2026-11-01", "date_to": "2026-09-01"},
        {"coordinates": {"lat": 100, "lon": 0}},
        {"unexpected": "attack"},
    ],
)
def test_invalid_intent(data):
    with pytest.raises(ValidationError):
        UserIntent(**data)


def test_request_validation_and_link_security():
    with pytest.raises(ValidationError):
        SearchRequest(query="ok", filters={})
    with pytest.raises(ValidationError):
        evidence().model_validate({**evidence().model_dump(), "source_url": "javascript:alert(1)"})
    with pytest.raises(ValidationError):
        Coordinates(lat=float("nan"), lon=0)
