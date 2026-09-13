"""Rebuild authored demo fixtures. Dates, prices and rubric inputs are illustrative."""

import json
from pathlib import Path

if __package__:
    from .visitor_guidance import visitor_documents
else:
    from visitor_guidance import visitor_documents

DATA = Path(__file__).resolve().parents[1] / "data"
STAMP = "2026-09-12T21:00:00+00:00"
docs = []


def doc(
    id,
    title,
    url,
    venue,
    category,
    text,
    field=None,
    value=None,
    sport="football",
    teams=None,
    authority="venue_official",
    effective=None,
):
    docs.append(
        dict(
            id=id,
            title=title,
            source_url=url,
            source_type=authority,
            sport=sport,
            league=None,
            teams=teams or [],
            venue=venue,
            category=category,
            text=text,
            field=field,
            value=value,
            publication_date=effective,
            effective_date=effective,
            ingestion_date=STAMP,
            authority=authority,
            event_id=None,
            event_type=None,
        )
    )


sj = "https://www.milb.com/san-jose/ballpark/a-z-guide"
sjp = "https://www.milb.com/san-jose/ballpark/play-it-safe-policies"
lev = "https://levisstadium.com/stadium-az-guide/"
levfood = "https://levisstadium.com/concessions/"
st = "https://gostanford.com/facilities/stanford-stadium"
mp = "https://gostanford.com/facilities/maples-pavilion"
cal = "https://calbears.com/sports/2026/8/3/cal-football-gameday-policies"
bay = "https://bayfc.com/paypal-park/a-z/"
sjsu = "https://sjsuspartans.com/cefcu-prohibited-items"
# Concise summaries only; no full-page copies. Unknown fields intentionally stay unknown.
doc(
    "sj-family",
    "A smaller ballpark, a family tradition",
    sj,
    "Excite Ballpark",
    "context",
    "The San Jose Giants describe their baseball experience as family-oriented. A Family Fun Zone is near the main entrance.",
    sport="baseball",
    teams=["San Jose Giants"],
)
doc(
    "sj-pathway",
    "The Giants development pathway",
    sj,
    "Excite Ballpark",
    "context",
    "San Jose is a Single-A affiliate of the San Francisco Giants.",
    sport="baseball",
    teams=["San Jose Giants"],
)
doc(
    "sj-water",
    "Excite Ballpark water rules",
    sj,
    "Excite Ballpark",
    "policy",
    "Unopened soft-sided water bottles and empty canteens are exceptions to the beverage restriction.",
    "water",
    sport="baseball",
)
doc(
    "sj-food-rule",
    "Excite Ballpark outside food",
    sj,
    "Excite Ballpark",
    "policy",
    "Outside food is generally prohibited. Exceptions include baby food, formula, medication and special needs.",
    "outside_food",
    sport="baseball",
)
doc(
    "sj-exceptions",
    "Children and medical needs",
    sj,
    "Excite Ballpark",
    "policy",
    "Medical necessities, including diaper bags, are exceptions to the clear-bag rule.",
    "exceptions",
    sport="baseball",
)
doc(
    "sj-reentry",
    "Excite Ballpark re-entry",
    sj,
    "Excite Ballpark",
    "policy",
    "Obtain a re-entry stamp near the main gate. On bobblehead giveaway days, re-entry starts after first pitch.",
    "reentry",
    sport="baseball",
)
doc(
    "sj-access",
    "Accessible seating at Excite",
    sj,
    "Excite Ballpark",
    "accessibility",
    "Wheelchair and companion seats are along the third-base line; purchase an accessible-seating ticket.",
    value={"wheelchair": True},
    sport="baseball",
)
doc(
    "sj-arrival",
    "Arrive for the opening gates",
    sj,
    "Excite Ballpark",
    "arrival",
    "General gates open one hour before game time.",
    sport="baseball",
)
doc(
    "sj-concessions",
    "Concessions at Excite",
    sj,
    "Excite Ballpark",
    "food",
    "The guide lists pizza, tacos and popcorn. Vegetarian ingredients and allergen suitability are not specified.",
    value={
        "vendor": "Pizza Stand / Third Base Taco Concession Booth",
        "vegetarian": None,
        "vegan": None,
        "gluten_free": None,
    },
    sport="baseball",
)
doc(
    "sj-bags",
    "Excite clear-bag policy",
    sjp,
    "Excite Ballpark",
    "policy",
    "Clear bags are required, with exceptions for small clutch purses and medically necessary items.",
    "bags",
    sport="baseball",
)
doc(
    "sj-prohibited",
    "Prohibited at Excite",
    sj,
    "Excite Ballpark",
    "policy",
    "Weapons, glass containers, hard-sided coolers and noisemakers are prohibited.",
    "prohibited",
    sport="baseball",
)
doc(
    "levis-food-rule",
    "Bring your own food",
    lev,
    "Levi’s Stadium",
    "policy",
    "Food must be in clear plastic wrapping or compliant clear bags.",
    "outside_food",
)
doc(
    "levis-water",
    "Water at Levi’s",
    lev,
    "Levi’s Stadium",
    "policy",
    "Only sealed plastic water bottles may be brought into the stadium.",
    "water",
)
doc(
    "levis-reentry",
    "Levi’s re-entry",
    lev,
    "Levi’s Stadium",
    "policy",
    "Re-entry is not permitted. For emergencies, contact gate security.",
    "reentry",
)
doc(
    "levis-vegan",
    "A verified plant-based option",
    levfood,
    "Levi’s Stadium",
    "food",
    "Stadium Favorites at section 129 West lists a Vegan Dog. Menu listings do not guarantee matchday availability.",
    value={
        "vendor": "Stadium Favorites — Vegan Dog",
        "location": "Section 129 West",
        "vegetarian": True,
        "vegan": True,
        "gluten_free": None,
    },
)
doc(
    "levis-context",
    "A 49ers home experience",
    lev,
    "Levi’s Stadium",
    "context",
    "The official stadium guide covers 49ers events and visitor facilities.",
    teams=["San Francisco 49ers"],
)
doc(
    "levis-access",
    "Accessible stadium restrooms",
    lev,
    "Levi’s Stadium",
    "accessibility",
    "Public restrooms are accessible. This does not verify accessible-seat inventory.",
    value={"accessible restrooms": True},
)
# Keep Oracle guide derivation under its restricted excerpt budget.
doc(
    "oracle-bags",
    "Oracle Park bags",
    "https://www.mlb.com/giants/ballpark/information/guide",
    "Oracle Park",
    "policy",
    "No backpacks. Other bags must be smaller than 16 × 16 × 8 inches.",
    "bags",
    sport="baseball",
)
doc(
    "oracle-tickets",
    "Prepare your mobile ticket",
    "https://www.mlb.com/giants/tickets/gameday",
    "Oracle Park",
    "arrival",
    "Download your mobile tickets before arrival. Ticket screenshots are not accepted.",
    sport="baseball",
)
doc(
    "biggame-history",
    "More than a game: the Big Game",
    "https://calbears.com/sports/2014/11/17/209769759",
    "California Memorial Stadium",
    "context",
    "The Cal–Stanford football rivalry began in 1892. The annual winner receives the Stanford Axe.",
    teams=["Stanford Cardinal", "California Golden Bears"],
    authority="official",
    effective="2014-11-17",
)
doc(
    "biggame-axe",
    "The story of the Axe",
    "https://calbears.com/sports/2014/11/17/209769759",
    "California Memorial Stadium",
    "context",
    "The Axe first appeared around a Stanford–Cal baseball game in 1899 and became the Big Game trophy in 1933.",
    teams=["Stanford Cardinal", "California Golden Bears"],
    authority="official",
    effective="2014-11-17",
)
doc(
    "stanford-bags",
    "Stanford Stadium entry",
    st,
    "Stanford Stadium",
    "policy",
    "Stanford Stadium enforces a clear-bag policy and security screening.",
    "bags",
    teams=["Stanford Cardinal"],
)
doc(
    "stanford-arrival",
    "Allow time for screening",
    st,
    "Stanford Stadium",
    "arrival",
    "Visitors pass through metal detectors. Check official updates before the event.",
)
doc(
    "maples-bags",
    "Maples Pavilion bags",
    mp,
    "Maples Pavilion",
    "policy",
    "Stanford’s clear-bag policy applies at Maples Pavilion.",
    "bags",
    sport="volleyball",
)
doc(
    "maples-context",
    "An indoor college-sports outing",
    mp,
    "Maples Pavilion",
    "context",
    "Maples Pavilion is an official Stanford athletics venue.",
    sport="volleyball",
    teams=["Stanford Cardinal"],
)
doc(
    "cal-bags",
    "Memorial Stadium entry policy",
    cal,
    "California Memorial Stadium",
    "policy",
    "A clear-bag policy applies and guests are subject to search.",
    "bags",
    effective="2026-08-03",
)
doc(
    "cal-food",
    "Food at Memorial Stadium",
    cal,
    "California Memorial Stadium",
    "policy",
    "Food is permitted; fruit must be cut into pieces.",
    "outside_food",
    effective="2026-08-03",
)
doc(
    "sjsu-bags",
    "CEFCU Stadium bag policy",
    sjsu,
    "CEFCU Stadium",
    "policy",
    "San Jose State enforces a clear-bag policy at CEFCU Stadium.",
    "bags",
)
doc(
    "sjsu-context",
    "College football in San Jose",
    "https://sjsuspartans.com/facilities/cefcu-stadium",
    "CEFCU Stadium",
    "context",
    "CEFCU Stadium is a San Jose State athletics venue and also hosts commencement ceremonies.",
    teams=["San Jose State Spartans"],
)
doc(
    "bay-context",
    "Make a day of a Bay FC match",
    "https://bayfc.com/matchday/know-before-you-go/",
    "PayPal Park",
    "context",
    "Bay FC FanFest offers activities for different ages and a rotating selection of food trucks.",
    sport="soccer",
    teams=["Bay FC"],
)
doc(
    "bay-arrival",
    "Your matchday companion",
    bay,
    "PayPal Park",
    "arrival",
    "The Bay FC app provides mobile-ticket management and a stadium guide.",
    sport="soccer",
)
doc(
    "bay-food",
    "Food trucks at FanFest",
    "https://bayfc.com/matchday/know-before-you-go/",
    "PayPal Park",
    "food",
    "FanFest has rotating food trucks. A specific vegetarian or vegan menu is not verified here.",
    value={"vendor": "Rotating FanFest food trucks", "vegetarian": None, "vegan": None, "gluten_free": None},
    sport="soccer",
)

doc(
    "sj-clutch-general",
    "Clutch size in the A–Z guide",
    sj,
    "Excite Ballpark",
    "policy",
    "The A–Z guide limits clutch purses to 4.5 × 6.5 inches.",
    "clutch_dimensions",
    value={"inches": [4.5, 6.5]},
    sport="baseball",
)
doc(
    "sj-clutch-entry",
    "Clutch size in entrance procedures",
    sjp,
    "Excite Ballpark",
    "policy",
    "Entrance procedures list a 5 × 9 inch clutch exception and a 12 × 6 × 12 inch clear-bag limit.",
    "clutch_dimensions",
    value={"inches": [5, 9]},
    sport="baseball",
)

levrules = "https://levisstadium.com/guest-services/permitted-prohibited-list/"
doc(
    "levis-bags",
    "Levi’s clear-bag dimensions",
    levrules,
    "Levi’s Stadium",
    "policy",
    "Clear bags may measure up to 12 × 6 × 12 inches; non-clear clutches up to 4.5 × 6.5 inches.",
    "bags",
)
doc(
    "levis-exceptions",
    "Medical and diaper bags",
    levrules,
    "Levi’s Stadium",
    "policy",
    "Diaper bags must accompany a child. Medical items require inspection and an inspection marker.",
    "exceptions",
)
doc(
    "levis-prohibited",
    "Items to leave at home",
    levrules,
    "Levi’s Stadium",
    "policy",
    "Weapons, cans, glass bottles, coolers and noisemakers are prohibited.",
    "prohibited",
)
doc(
    "levis-water-list",
    "Water containers on the permitted list",
    levrules,
    "Levi’s Stadium",
    "policy",
    "The permitted-items list allows sealed plastic and reusable transparent water bottles smaller than 24 ounces. This differs from the A–Z wording.",
    "water",
)
doc(
    "bay-bags",
    "PayPal Park clear bags",
    bay,
    "PayPal Park",
    "policy",
    "Clear bags up to 12 × 12 × 6 inches and clutches up to 4.5 × 6.5 inches are allowed.",
    "bags",
    sport="soccer",
)
doc(
    "bay-water",
    "Water at PayPal Park",
    bay,
    "PayPal Park",
    "policy",
    "Bring one sealed, unflavored still-water plastic bottle up to 32 ounces, or one empty clear reusable plastic bottle per person.",
    "water",
    sport="soccer",
)
doc(
    "bay-outside-food",
    "Small snacks at PayPal Park",
    bay,
    "PayPal Park",
    "policy",
    "Small individual snacks in clear bags are permitted; large outside meals and coolers are not.",
    "outside_food",
    sport="soccer",
)
doc(
    "bay-exceptions",
    "Child and dietary exceptions",
    bay,
    "PayPal Park",
    "policy",
    "Diaper bags require an accompanying child. Ask Guest Experience about exceptions for children and dietary or medical needs.",
    "exceptions",
    sport="soccer",
)
doc(
    "bay-reentry",
    "PayPal Park re-entry",
    bay,
    "PayPal Park",
    "policy",
    "Re-entry requires gate-supervisor authorization for an emergency.",
    "reentry",
    sport="soccer",
)
doc(
    "bay-prohibited",
    "PayPal Park prohibited items",
    bay,
    "PayPal Park",
    "policy",
    "Glass or metal water bottles, weapons, umbrellas and strollers are prohibited.",
    "prohibited",
    sport="soccer",
)

rows = [
    (
        "sj-giants",
        "San Jose Giants vs. Stockton Ports",
        "baseball",
        "MiLB",
        "local",
        ["San Jose Giants", "Stockton Ports"],
        "2026-09-19T17:00:00-07:00",
        "Excite Ballpark",
        "San Jose",
        37.3215,
        -121.8623,
        14,
        24,
        36,
        52,
        78,
        96,
        "relaxed",
        "orange",
        ["family experience", "local tradition"],
        sj,
    ),
    (
        "sf-giants",
        "San Francisco Giants vs. Los Angeles Dodgers",
        "baseball",
        "MLB",
        "professional",
        ["San Francisco Giants", "Los Angeles Dodgers"],
        "2026-09-19T18:05:00-07:00",
        "Oracle Park",
        "San Francisco",
        37.7786,
        -122.3893,
        65,
        140,
        65,
        94,
        95,
        72,
        "electric",
        "orange",
        ["rivalry", "unusual venue"],
        "https://www.mlb.com/giants/schedule",
    ),
    (
        "49ers",
        "San Francisco 49ers vs. Seattle Seahawks",
        "football",
        "NFL",
        "professional",
        ["San Francisco 49ers", "Seattle Seahawks"],
        "2026-09-20T13:25:00-07:00",
        "Levi’s Stadium",
        "Santa Clara",
        37.403,
        -121.97,
        175,
        320,
        100,
        96,
        98,
        62,
        "electric",
        "red",
        ["rivalry", "strong atmosphere"],
        lev,
    ),
    (
        "big-game",
        "Cal vs. Stanford · The Big Game",
        "football",
        "NCAA",
        "college",
        ["California Golden Bears", "Stanford Cardinal"],
        "2026-11-21T12:30:00-08:00",
        "California Memorial Stadium",
        "Berkeley",
        37.871,
        -122.2508,
        75,
        150,
        65,
        100,
        97,
        70,
        "electric",
        "blue",
        ["rivalry", "local tradition"],
        "https://calbears.com/sports/2014/11/17/209769759",
    ),
    (
        "sjsu",
        "San Jose State vs. Fresno State",
        "football",
        "NCAA",
        "college",
        ["San Jose State Spartans", "Fresno State Bulldogs"],
        "2026-09-19T16:00:00-07:00",
        "CEFCU Stadium",
        "San Jose",
        37.3196,
        -121.8683,
        22,
        45,
        30,
        75,
        81,
        80,
        "electric",
        "blue",
        ["rivalry", "local tradition"],
        sjsu,
    ),
    (
        "stanford-volleyball",
        "Stanford vs. Cal · Women’s Volleyball",
        "volleyball",
        "NCAA",
        "college",
        ["Stanford Cardinal", "California Golden Bears"],
        "2026-09-20T14:00:00-07:00",
        "Maples Pavilion",
        "Stanford",
        37.4293,
        -122.1608,
        12,
        20,
        28,
        75,
        82,
        86,
        "electric",
        "red",
        ["rivalry", "affordability"],
        mp,
    ),
    (
        "bay-fc",
        "Bay FC vs. Angel City FC",
        "soccer",
        "NWSL",
        "professional",
        ["Bay FC", "Angel City FC"],
        "2026-09-19T19:00:00-07:00",
        "PayPal Park",
        "San Jose",
        37.3516,
        -121.925,
        28,
        60,
        45,
        76,
        86,
        85,
        "electric",
        "navy",
        ["family experience", "strong atmosphere"],
        bay,
    ),
    (
        "stanford-football",
        "Stanford vs. Notre Dame",
        "football",
        "NCAA",
        "college",
        ["Stanford Cardinal", "Notre Dame Fighting Irish"],
        "2026-11-28T12:30:00-08:00",
        "Stanford Stadium",
        "Stanford",
        37.4346,
        -122.161,
        55,
        115,
        60,
        89,
        88,
        73,
        "electric",
        "red",
        ["rivalry", "local tradition"],
        st,
    ),
]
events = []
for r in rows:
    (
        id,
        name,
        sport,
        league,
        level,
        teams,
        start,
        venue,
        city,
        lat,
        lon,
        pmin,
        pmax,
        extra,
        sig,
        exp,
        family,
        atmo,
        color,
        signals,
        url,
    ) = r
    source = f"/api/demo/fixtures/{id}"
    claim = f"Illustrative fixture: {name}; date, opponent, ticket range, outing allowance and editorial scores are scenario assumptions, not a verified listing."
    ev = dict(
        id=id,
        provider="demo",
        provider_event_id=id,
        name=name,
        sport=sport,
        league=league,
        level=level,
        teams=teams,
        start_time=start,
        venue=venue,
        city=city,
        coordinates={"lat": lat, "lon": lon},
        price_min=pmin,
        price_max=pmax,
        outing_extra=extra,
        price_basis="illustrative",
        ticket_url=url,
        source_url=source,
        retrieved_at=STAMP,
        verification="illustrative",
        data_mode="illustrative",
        signals=signals,
        significance=sig,
        experience=exp,
        family=family,
        atmosphere=atmo,
        color=color,
        evidence=[
            dict(
                id=f"fixture-{id}",
                claim=claim,
                category="fixture",
                source_id=f"fixture-{id}",
                source_title="Illustrative scenario assumptions",
                source_url=source,
                authority="illustrative",
                retrieved_at=STAMP,
                freshness="illustrative",
                confidence=0.5,
            )
        ],
    )
    events.append(ev)
(DATA / "demo" / "events.json").write_text(json.dumps(events, indent=2, ensure_ascii=False) + "\n")
docs.extend(visitor_documents())
(DATA / "knowledge" / "corpus.json").write_text(json.dumps(docs, indent=2, ensure_ascii=False) + "\n")
(DATA / "local_events" / "events.json").write_text("[]\n")
print(f"Wrote {len(events)} illustrative events and {len(docs)} sourced documents.")
