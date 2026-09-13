# Inventory and knowledge curation

The shipped demo has eight authored fixtures across professional football/baseball, minor-league baseball, college football, women’s college volleyball and women’s professional soccer. Opponents and stadiums are plausible, but **none of the dated demo fixtures are verified events**. Do not turn `illustrative` into `verified` without checking an official schedule and ticket/access information.

The fixture endpoint provides each scenario’s provenance and exact inputs. `scripts/seed_data.py` regenerates those authored files. It is not a live-ingestion or source-refresh tool; its fixed September 12, 2026 ingestion date records the source-review session. It must not update freshness simply because the script was rerun.

## Adding a verified local event

Add a full `EventCandidate` object to `backend/data/local_events/events.json`. Validate with the Pydantic model before presenting. Include:

1. Official confirmed date, time, timezone, venue and coordinates, plus public spectator access.
2. A direct official event/schedule URL and a ticket/info URL. Preserve provider and provider-event IDs.
3. `data_mode: curated`, `verification: verified`, retrieval timestamp and at least one compelling signal.
4. A cited `EvidenceItem` for the signal and any assigned rubric input. Do not assign missing factors 50 or invent prices. Keep unsupported values null.
5. Prefer the official single-event instructions over a venue-wide guide. Store exceptions and conflicts explicitly.

Past or unverified records are rejected. Hybrid excludes all illustrative fixtures and initially has **no verified curated records**; without supplied enrichment it may return no qualifying events. This is an intentional accuracy boundary, not complete live coverage. Ticketmaster records with equivalent venue/time/team identity are merged with reviewed curated signal evidence.

## Knowledge corpus

64 concise documents cover Excite Ballpark, Oracle Park, Levi’s Stadium, Stanford Stadium, Maples Pavilion, Memorial Stadium, CEFCU Stadium, PayPal Park, Giants development context, the Big Game/Axe, college venues and Bay FC.

Sources were accessed from official venue/team/college domains on September 12, 2026. Historical material is marked as historical; publication/effective dates are null where unavailable. These are concise factual summaries, not full-page copies. Examples:

- [San Jose Giants A–Z guide](https://www.milb.com/san-jose/ballpark/a-z-guide)
- [Excite entrance procedures](https://www.milb.com/san-jose/ballpark/play-it-safe-policies)
- [Levi’s A–Z guide](https://levisstadium.com/stadium-az-guide/)
- [Levi’s permitted/prohibited list](https://levisstadium.com/guest-services/permitted-prohibited-list/)
- [Levi’s concessions](https://levisstadium.com/concessions/)
- [Cal Big Game history](https://calbears.com/sports/2014/11/17/209769759)
- [Stanford Maples Pavilion](https://gostanford.com/facilities/maples-pavilion)
- [Bay FC PayPal Park guide](https://bayfc.com/paypal-park/a-z/)

The San Jose sources disagree about clutch dimensions. Levi’s official pages differ on water-container wording. Both conflicts remain in the corpus and are surfaced by the policy resolver. No model or curator silently declares one unambiguous.

After an actual review, edit the factual summary, source, metadata and ingestion timestamp, then run `uv run python -m scripts.ingest`. The fingerprint detects changed content. Use `--lexical` only for development fallback; it does not make agent preflight ready.

Dietary data deliberately records null rather than inferring ingredients from names like “pizza.” The Levi’s menu explicitly lists a vegan dog; the Excite guide lists concessions without confirming vegetarian ingredients. No allergy-safe claim is made. Availability of a menu item or accessible seat on a particular date is not guaranteed.

## Parking, seating and attire

Seventeen visitor summaries were added on September 12, 2026 (Pacific Time), covering parking and seating convenience for all eight demo venues. `backend/scripts/visitor_guidance.py` preserves the exact review timestamp; running it as a module merges these entries without changing event inventory. The full seed script also includes them.

The San Jose parking section still describes 2025. Its summary explicitly identifies that season and sets `needs_recheck: true`, so a recent review never makes those old arrangements look current. No parking prices, inventory, walking times, seat availability, shade or sightlines are inferred. Other operational visitor summaries expire after 90 days.

Additional sources include [Giants accessible transportation](https://www.mlb.com/giants/ballpark/transportation/accessible), [Giants accessible services](https://www.mlb.com/giants/ballpark/accessible-services), [Levi’s parking](https://levisstadium.com/plan-your-visit/parking/), [Levi’s accessible services](https://levisstadium.com/guest-services/ada-services/), [Cal parking](https://calbears.com/sports/2026/7/30/football-gameday-parking-transportation), [Cal accessibility](https://calbears.com/sports/2026/8/3/cal-football-accessibility), [CEFCU facility guidance](https://sjsuspartans.com/facilities/cefcu-stadium), [Bay FC matchday guidance](https://bayfc.com/articles/the-official-bay-fc-matchday-guide-20260126/), and [Stanford football gameday](https://gostanford.com/stanford-football-gameday-central).

Attire and seat-choosing tips are authored comfort suggestions, visibly separate from cited venue facts. They do not themselves represent a dress code or weather forecast, live seat recommendation or accessible-seat reservation. Parking guidance does not change the illustrative outing allowance or the ranking.

## Weather and clothing rules

Three additional attire entries document umbrella restrictions at Excite Ballpark and PayPal Park, and clothing/umbrella restrictions at Levi’s Stadium. They retain their own review timestamp and citations; uncurated venues display an information gap. Guidance never infers an event-specific exception from a general rule.

Weather is retrieved separately from [Open-Meteo’s forecast API](https://open-meteo.com/en/docs), using venue coordinates and UTC timestamps. It is not part of the stored venue corpus. Hourly Fahrenheit temperature, feels-like temperature, precipitation probability and wind in mph are summarized over four hourly samples spanning three hours around the start. This planning window does not claim to cover the full event. The UI attributes Open-Meteo, dates the retrieval and identifies illustrative fixture dates.

Suggestions use feels-like temperature (below 50°F: warm jacket; below 65°F: light jacket; 80°F or above: breathable clothing), hourly rain chance of at least 30%, and wind of at least 15 mph. These are editorial comfort thresholds, not medical advice or venue rules. Verified umbrella restrictions inform the rain-layer suggestion; the full sourced restrictions appear immediately below it. Indoor temperatures and seat-level microclimates are not inferred.
