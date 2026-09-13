from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.models.domain import EventCandidate, EvidenceItem, ScoreBreakdown, UserIntent
from app.providers.distance import HaversineDistanceProvider

WEIGHTS = {
    "user_fit": 0.25,
    "significance": 0.20,
    "experience": 0.15,
    "convenience": 0.15,
    "value": 0.15,
    "personal_needs": 0.10,
}


def eligibility(event: EventCandidate, allow_illustrative: bool = True) -> list[str]:
    reasons = []
    if not event.public_access or not event.spectator_event:
        reasons.append("Not a public spectator event")
    if not event.date_confirmed or not event.venue_confirmed:
        reasons.append("Date or venue unconfirmed")
    if event.verification in {"unverified", "outdated"}:
        reasons.append("Event is unverified or outdated")
    if event.data_mode == "illustrative" and not allow_illustrative:
        reasons.append("Illustrative fixtures excluded from hybrid inventory")
    if not event.source_url or not event.signals or not event.evidence:
        reasons.append("Insufficient source evidence or attendance signals")
    if event.data_mode != "illustrative" and event.start_time < datetime.now(timezone.utc):
        reasons.append("Event has already occurred")
    return reasons


def distance(event: EventCandidate, intent: UserIntent) -> float | None:
    if intent.coordinates:
        return HaversineDistanceProvider().miles(intent.coordinates, event.coordinates)
    return None


def estimated_total(event: EventCandidate, intent: UserIntent) -> float | None:
    if event.price_min is None or event.outing_extra is None:
        return None
    return round(event.price_min * (intent.adults + intent.children) + event.outing_extra, 2)


def hard_filters(event: EventCandidate, intent: UserIntent) -> list[str]:
    reasons = []
    day = event.start_time.astimezone(ZoneInfo(event.timezone)).date()
    if intent.date_from and day < intent.date_from or intent.date_to and day > intent.date_to:
        reasons.append("Outside your date range")
    miles = distance(event, intent)
    if intent.radius_miles is not None and (miles is None or miles > intent.radius_miles):
        reasons.append("Outside your radius" if miles is not None else "Location could not be resolved")
    if intent.sports and event.sport.lower() not in [s.lower() for s in intent.sports]:
        reasons.append("Does not match your sport")
    if intent.teams and not any(t.lower() in team.lower() for t in intent.teams for team in event.teams):
        reasons.append("Does not match your team")
    if not intent.local_openness and event.level != "professional":
        reasons.append("You requested major professional events only")
    if intent.budget is not None:
        cost = event.price_min if intent.budget_type == "per_ticket" else estimated_total(event, intent)
        if cost is None:
            reasons.append("Price or total outing cost unverified for your hard budget")
        elif cost > intent.budget:
            reasons.append("Over your budget")
    return reasons


def need_filters(intent: UserIntent, evidence: list[EvidenceItem]) -> list[str]:
    reasons = []
    if intent.dietary_required:
        for need in intent.dietary:
            key = need.lower().replace("-", "_")
            if not any(
                e.category == "food"
                and isinstance(e.value, dict)
                and e.value.get(key) is True
                and e.freshness == "current"
                and e.confidence >= 0.8
                for e in evidence
            ):
                reasons.append(f"Required {need} option is not verified")
    for need in intent.accessibility:
        if not any(
            e.category == "accessibility"
            and isinstance(e.value, dict)
            and e.value.get(need.lower()) is True
            and e.freshness == "current"
            for e in evidence
        ):
            reasons.append(f"Required accessibility need is not verified: {need}")
    return reasons


def score(event: EventCandidate, intent: UserIntent, evidence: list[EvidenceItem]) -> ScoreBreakdown:
    factors: dict[str, float | None] = {k: None for k in WEIGHTS}
    rationale = {}
    fit = []
    if intent.sports:
        fit.append(100.0)
    if intent.teams:
        fit.append(100.0)
    if intent.atmosphere != "any":
        if intent.atmosphere == "iconic":
            fit.append(event.significance)
        elif intent.atmosphere == "rivalry":
            fit.append(100.0 if "rivalry" in event.signals else 20.0)
        else:
            fit.append(100.0 if event.atmosphere == intent.atmosphere else 35.0)
    if intent.family_friendly or intent.children:
        fit.append(event.family)
    if [x for x in fit if x is not None]:
        factors["user_fit"] = sum(x for x in fit if x is not None) / len([x for x in fit if x is not None])
    factors["significance"] = event.significance
    factors["experience"] = event.experience
    d = distance(event, intent)
    # Convenience is irrelevant when the user explicitly has no distance preference.
    if d is not None and intent.radius_miles is not None:
        factors["convenience"] = max(0.0, 100 * (1 - d / intent.radius_miles))
    cost = event.price_min if intent.budget_type == "per_ticket" else estimated_total(event, intent)
    if intent.budget is not None and cost is not None:
        factors["value"] = (
            100.0 if intent.budget == 0 and cost == 0 else max(0.0, 100 * (1 - cost / max(intent.budget, 1)))
        )
    needs = []
    if intent.children or intent.family_friendly:
        needs.append(event.family)
    for diet in intent.dietary:
        found = any(
            e.category == "food"
            and isinstance(e.value, dict)
            and e.value.get(diet.lower().replace("-", "_")) is True
            and e.freshness == "current"
            for e in evidence
        )
        needs.append(100.0 if found else None)
    for need in intent.accessibility:
        needs.append(
            100.0
            if not need_filters(
                intent.model_copy(update={"dietary_required": False, "accessibility": [need]}), evidence
            )
            else None
        )
    # If any requested need lacks evidence, do not manufacture an aggregate needs score.
    if needs and all(x is not None for x in needs):
        factors["personal_needs"] = sum(needs) / len(needs)
    available = sum(WEIGHTS[k] for k, v in factors.items() if v is not None)
    weights = {k: round(WEIGHTS[k] / available, 6) if v is not None and available else 0.0 for k, v in factors.items()}
    opportunity = round(sum(v * weights[k] for k, v in factors.items() if v is not None), 1)
    missing = [k for k, v in factors.items() if v is None]
    for k, v in factors.items():
        rationale[k] = (
            "Unavailable or not relevant; remaining weights normalized proportionally."
            if v is None
            else "Deterministic from validated preferences and cited inputs."
        )
    rationale["significance"] = (
        "Editorial fixture rubric, not a live competitive statistic."
        if event.data_mode == "illustrative"
        else "Source-backed competitive and cultural signals."
    )
    rationale["value"] = "Budget remaining after the modeled cost; not a ticket availability guarantee."
    relevant_categories = {"context", "policy"}
    if intent.dietary:
        relevant_categories.add("food")
    if intent.accessibility:
        relevant_categories.add("accessibility")
    coverage = sum(any(e.category == c for e in evidence) for c in relevant_categories) / len(relevant_categories)
    quality = (
        sum(e.confidence * (0.45 if e.freshness == "stale" else 1) for e in evidence) / len(evidence) if evidence else 0
    )
    confidence = round(100 * (0.45 * quality + 0.35 * coverage + 0.20 * available))
    if intent.dietary and factors["personal_needs"] is None:
        confidence -= 15
    if event.data_mode == "illustrative":
        confidence = min(confidence, 75)
    if cost is None:
        confidence -= 8
    return ScoreBreakdown(
        factors=factors,
        weights=weights,
        opportunity_score=opportunity,
        evidence_confidence=max(0, min(100, confidence)),
        missing_factors=missing,
        rationale=rationale,
    )


def rank(events: list[EventCandidate], intent: UserIntent, evidence: dict[str, list[EvidenceItem]]):
    scored = [(e, score(e, intent, evidence.get(e.id, []))) for e in events]
    return sorted(scored, key=lambda x: (-x[1].opportunity_score, -x[1].evidence_confidence, x[0].start_time, x[0].id))
