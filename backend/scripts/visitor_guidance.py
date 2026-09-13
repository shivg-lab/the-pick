"""Authored visitor summaries reviewed September 12, 2026 (Pacific Time).

Running this module merges only these summaries; it never changes event inventory.
"""

import json
from pathlib import Path

REVIEWED = "2026-09-13T01:42:22+00:00"
SJ = "https://www.milb.com/san-jose/ballpark/a-z-guide"
MAPLES = "https://gostanford.com/facilities/maples-pavilion"
BAY = "https://bayfc.com/paypal-park/a-z/"
CEFCU = "https://sjsuspartans.com/facilities/cefcu-stadium"
STANFORD = "https://gostanford.com/stanford-football-gameday-central"

# Clothing/umbrella facts remain distinct from authored comfort advice.
ATTIRE_SUMMARIES = [
    (
        "sj-attire",
        "Excite Ballpark",
        "baseball",
        "attire",
        SJ,
        "Umbrellas may be brought in subject to size restrictions, but cannot be opened in seating areas or obstruct other spectators' views.",
    ),
    (
        "bay-attire",
        "PayPal Park",
        "soccer",
        "attire",
        BAY,
        "Umbrellas are prohibited at PayPal Park. Choose another rain-protection option for your visit.",
    ),
    (
        "levis-attire",
        "Levi’s Stadium",
        "football",
        "attire",
        "https://levisstadium.com/guest-services/permitted-prohibited-list/",
        "Umbrellas must not obstruct other fans' views. Offensive clothing and light-up costumes are prohibited. Identity-concealing hoods or masks are restricted, with medical and religious exceptions; check the official wording.",
    ),
]

# id, venue, sport, category, source URL, concise paraphrase
SUMMARIES = [
    (
        "sj-parking",
        "Excite Ballpark",
        "baseball",
        "parking",
        SJ,
        "The guide's 2025 parking section lists the Main Lot, SJSU Golf Lot and Happy Hollow K1 Lot on Senter Road. Lots are first come, first served; Friday fireworks restrict the Main Lot to season-ticket parking passes. Confirm this season's arrangements; current prices are unverified.",
    ),
    (
        "sj-seating",
        "Excite Ballpark",
        "baseball",
        "seating",
        SJ,
        "Wheelchair and companion seating is along the third-base line and requires an accessible-seating ticket. Restrooms are on the main concourse, first-base side and in left field beyond the BBSI Futures Club.",
    ),
    (
        "oracle-parking",
        "Oracle Park",
        "baseball",
        "parking",
        "https://www.mlb.com/giants/ballpark/transportation/accessible",
        "Giants-controlled parking requires a SpotHero reservation, including for ADA placard holders. An accessibility shuttle connects Lot A/Pier 48 with the ballpark.",
    ),
    (
        "oracle-seating",
        "Oracle Park",
        "baseball",
        "seating",
        "https://www.mlb.com/giants/ballpark/accessible-services",
        "Use the Accessibility filter when buying Giants tickets online to find accessible seating.",
    ),
    (
        "levis-parking",
        "Levi’s Stadium",
        "football",
        "parking",
        "https://levisstadium.com/plan-your-visit/parking/",
        "Parking prices vary by event. Event-day credit-card lots are limited and may cost more than prepaid parking. Use the official parking page to select your event and review its lot map.",
    ),
    (
        "levis-accessible-parking",
        "Levi’s Stadium",
        "football",
        "parking",
        "https://levisstadium.com/stadium-az-guide/",
        "Accessible parking uses the Red Lot 1 entrance, with a valid DMV placard or plate and a parking pass. Event-day passes and accessible spaces are subject to availability; check the official instructions before arrival.",
    ),
    (
        "levis-seating",
        "Levi’s Stadium",
        "football",
        "seating",
        "https://levisstadium.com/guest-services/ada-services/",
        "Accessible and companion seats are offered in multiple areas. Public elevators and escalators serve Gates A, C and F. For 49ers games, arrange accessible-seat exchanges before event day; same-day exchanges are unavailable.",
    ),
    (
        "cal-parking",
        "California Memorial Stadium",
        "football",
        "parking",
        "https://calbears.com/sports/2026/7/30/football-gameday-parking-transportation",
        "Public UC parking includes Lower Hearst Level 2, Genetics, Lower Sproul and Bancroft structures, on a first-come basis. Most nearby residential street parking requires a permit. Check the official parking map, game-day road closures and shuttle instructions before driving.",
    ),
    (
        "cal-seating",
        "California Memorial Stadium",
        "football",
        "seating",
        "https://calbears.com/sports/2026/8/3/cal-football-accessibility",
        "Accessible seats are distributed around the bowl. The East Rim has no elevator access, so check the official gate-to-seat route map before booking. Family restrooms are near sections KK, EE and C.",
    ),
    (
        "cefcu-parking",
        "CEFCU Stadium",
        "football",
        "parking",
        CEFCU,
        "Tailgate parking is listed at the SJSU Park and Ride lot on 7th Street. Overflow options include the 10th and Alma garage and the 7th and San Salvador garage. Confirm game-day lot access, pricing and shuttle operation.",
    ),
    (
        "cefcu-seating",
        "CEFCU Stadium",
        "football",
        "seating",
        CEFCU,
        "The facility guide permits seat cushions without pockets, arms or zippers. Specific seat backs, stair access and accessible-seat availability are not verified here; ask the ticket office before choosing seats.",
    ),
    (
        "maples-parking",
        "Maples Pavilion",
        "volleyball",
        "parking",
        MAPLES,
        "Parking Structure 7 is across Campus Drive. Lot 11 beside the arena is reserved for season-ticket holders; the Varsity and Visitor Center lots provide additional options. Check current campus restrictions and event instructions.",
    ),
    (
        "maples-seating",
        "Maples Pavilion",
        "volleyball",
        "seating",
        MAPLES,
        "Lower-level seats are padded with backs; upper-level molded plastic seats have no backs. Accessible seating is distributed through the venue, with a southwest-corner elevator serving lower seating.",
    ),
    (
        "bay-parking",
        "PayPal Park",
        "soccer",
        "parking",
        "https://bayfc.com/articles/the-official-bay-fc-matchday-guide-20260126/",
        "Bay FC parking can be bought in advance through Tixr or from an attendant at the lot on matchday. Use the official matchday guide for the parking link and current arrangements.",
    ),
    (
        "bay-seating",
        "PayPal Park",
        "soccer",
        "seating",
        BAY,
        "Accessible seats are offered across areas and price levels. Elevators are behind sections 107 and 122; wheelchair lifts serve front accessible seating at sections 114 and 132. Contact Bay FC to arrange suitable tickets.",
    ),
    (
        "stanford-parking",
        "Stanford Stadium",
        "football",
        "parking",
        STANFORD,
        "Football parking requires a pass for the correct lot. On-site payment is offered only at General Lots 7 and 8 and IM South Lot 4; those transactions do not accept cash. Check your game's parking map before arrival.",
    ),
    (
        "stanford-seating",
        "Stanford Stadium",
        "football",
        "seating",
        "https://gostanford.com/facilities/stanford-stadium",
        "The family restroom is behind section 103 in the south guest-service room. Use the entrance nearest your section for easier access; the official facility page links a 3D seating map.",
    ),
]


def visitor_documents():
    return [
        dict(
            id=id,
            title=f"{venue}: {category} guidance",
            source_url=url,
            source_type="venue_official",
            sport=sport,
            league=None,
            teams=[],
            venue=venue,
            category=category,
            text=claim,
            field=None,
            value={"umbrella_use": "prohibited" if id == "bay-attire" else "restricted"}
            if category == "attire"
            else None,
            publication_date=None,
            effective_date=None,
            ingestion_date="2026-09-13T01:54:11+00:00" if category == "attire" else REVIEWED,
            authority="venue_official",
            event_id=None,
            event_type=sport,
            needs_recheck=id == "sj-parking",
        )
        for id, venue, sport, category, url, claim in SUMMARIES + ATTIRE_SUMMARIES
    ]


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "data/knowledge/corpus.json"
    additions = visitor_documents()
    ids = {d["id"] for d in additions}
    existing = [d for d in json.loads(path.read_text()) if d["id"] not in ids]
    path.write_text(json.dumps(existing + additions, indent=2, ensure_ascii=False) + "\n")
    print(f"Merged {len(additions)} visitor summaries; {len(existing) + len(additions)} documents total.")
