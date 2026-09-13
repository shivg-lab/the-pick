from app.models.domain import EventCandidate, EventGuide, EventWeather, EvidenceItem, FoodOption, VenuePolicy

from app.services.attire import attire_suggestions

PRECEDENCE = {
    "event_official": 0,
    "team_official": 1,
    "venue_official": 2,
    "official": 2,
    "trusted": 3,
    "illustrative": 4,
}
POLICY_FIELDS = ["bags", "outside_food", "water", "exceptions", "prohibited", "reentry"]
CONFLICT = "The event-specific instructions and the venue’s general policy appear inconsistent. Confirm with the venue before attending."


def resolve_policies(event: EventCandidate, evidence: list[EvidenceItem]) -> VenuePolicy:
    grouped: dict[str, list[EvidenceItem]] = {}
    for item in evidence:
        if item.category != "policy" or not item.field or item.venue != event.venue:
            continue
        if item.event_id and item.event_id != event.id or item.event_type and item.event_type != event.sport:
            continue
        grouped.setdefault(item.field, []).append(item)
    fields, conflicts, warnings = {}, [], []
    for key, items in grouped.items():
        items.sort(key=lambda x: (x.freshness == "stale", PRECEDENCE[x.authority], -x.retrieved_at.timestamp()))
        fields[key] = items[0]
        signatures = {str(x.value if x.value is not None else x.claim).lower().strip() for x in items}
        if len(signatures) > 1:
            conflicts.append(
                CONFLICT
                if any(x.authority == "event_official" for x in items)
                else f"Official sources disagree about {key.replace('_', ' ')}. Confirm with the venue before attending."
            )
        if items[0].freshness == "stale":
            warnings.append(
                f"{key.replace('_', ' ').capitalize()} policy is older than 90 days; recheck before attending."
            )
    for key in POLICY_FIELDS:
        if key not in fields:
            warnings.append(f"{key.replace('_', ' ').capitalize()}: not verified in the current corpus.")
    return VenuePolicy(
        venue=event.venue,
        fields=fields,
        conflicts=conflicts,
        warnings=warnings,
        last_verified=min((e.retrieved_at.date() for e in fields.values()), default=None),
    )


def generate_guide(
    event: EventCandidate, evidence: list[EvidenceItem], weather: EventWeather | None = None
) -> EventGuide:
    evidence = [
        e
        for e in evidence
        if e.venue == event.venue
        and (not e.event_id or e.event_id == event.id)
        and (not e.event_type or e.event_type == event.sport)
    ]
    policy = resolve_policies(event, evidence)
    food = []
    for e in evidence:
        if e.category == "food" and isinstance(e.value, dict):
            v = e.value
            food.append(
                FoodOption(
                    venue=event.venue,
                    vendor=v.get("vendor", "Official concessions"),
                    location=v.get("location"),
                    vegetarian=v.get("vegetarian"),
                    vegan=v.get("vegan"),
                    gluten_free=v.get("gluten_free"),
                    evidence=e,
                )
            )
    warnings = list(policy.warnings) + list(policy.conflicts)
    if not food:
        warnings.append("Dietary options are not verified in the current corpus. Contact the venue.")
    warnings.append(
        "These are stored official-source summaries, not event-day verification. Recheck the official guide."
    )
    preparation = {category: [e for e in evidence if e.category == category] for category in ("parking", "seating")}
    for category, items in preparation.items():
        if not items:
            warnings.append(
                f"{category.capitalize()} details are not verified for this venue. Check the official guide."
            )
        elif any(e.freshness == "stale" for e in items):
            warnings.append(
                f"{category.capitalize()} guidance includes an older source; confirm current event arrangements."
            )
    return EventGuide(
        policy=policy,
        food=food,
        arrival=[e.claim for e in evidence if e.category == "arrival"],
        **preparation,
        weather=weather or EventWeather(),
        attire_rules=[e for e in evidence if e.category == "attire"],
        attire_tips=attire_suggestions(weather or EventWeather(), [e for e in evidence if e.category == "attire"]),
        seating_tip="For easier breaks, compare aisle seats and proximity to restrooms or concessions. Confirm seat backs, steps, accessible routes and any shade with the ticket office before booking.",
        warnings=warnings,
    )
