# The Pick — full narrated demo

Share **the-pick-demo.mp4**: 5:16, 26.2 MB. H.264 video, 1440 × 1000, 25 fps, AAC audio. Includes synthetic spoken narration and on-screen chapter captions. A full transcript and optional SRT subtitles are included.

Both searches use the real local app and Ollama agent. Only the middle of long inference waits is removed; results are not mocked. Event dates, matchups and prices are illustrative. Venue guidance retains source links and review dates; weather uses the live provider when a forecast is available. Narration is generated locally with the macOS Samantha voice.

## Chapters

- 0:00 — **THE PICK**: Discover. Decide. Prepare.
- 0:11 — **FAMILY ON A BUDGET**: Two adults, two children, $120 total.
- 0:21 — **MAKE IT YOUR DAY**: Adjust location, budget, distance and personal needs.
- 0:33 — **THE LOCAL AGENT**: Investigating real sources · waiting time shortened.
- 0:47 — **YOUR FAMILY PICK**: One prominent winner, with clear reasons.
- 0:57 — **THE EVENT, AT A GLANCE**: Venue, date, distance, ticket price and outing estimate.
- 1:09 — **SHOW YOUR WORK**: Inspect the score, factors and weights.
- 1:20 — **ALSO WORTH SHOWING UP FOR**: Two smaller alternatives to compare.
- 1:29 — **KNOW BEFORE YOU GO**: Practical guidance directly beneath the winner.
- 1:39 — **THE FULL VENUE GUIDE**: Bag policy, outside food and source conflicts.
- 1:50 — **PACK WITH CONFIDENCE**: Water, children’s needs, prohibited items and re-entry.
- 2:01 — **FOOD & ARRIVAL**: Dietary preferences, concessions and information gaps.
- 2:13 — **GETTING THERE**: Arrival guidance and honest distance estimates.
- 2:24 — **PARKING & COMFORT**: Parking locations, booking guidance and older sources.
- 2:35 — **FIND A COMFORTABLE SEAT**: Accessible seating, nearby amenities and practical tips.
- 2:47 — **WEATHER FOR YOUR OUTING**: Real forecast near the event’s start time.
- 2:58 — **WHAT TO WEAR**: Weather-informed suggestions plus official venue rules.
- 3:10 — **CHECK THE SOURCES**: Official links, review dates and evidence provenance.
- 3:21 — **HELP IMPROVE THE NEXT PICK**: Rate the outing and report corrections.
- 3:31 — **THE ICONIC EXPERIENCE**: A different goal, with no budget or distance limit.
- 3:40 — **A DIFFERENT INVESTIGATION**: History, rivalry and significance · waiting time shortened.
- 3:53 — **YOUR ICONIC PICK**: Cal versus Stanford: The Big Game.
- 4:04 — **UNDERSTAND THE TRADEOFFS**: Inspect this event’s venue, cost and supporting reasons.
- 4:14 — **A GUIDE FOR THIS VENUE**: Memorial Stadium’s policies and food information.
- 4:26 — **PLAN THE BIG DAY**: Venue-specific parking and accessible routes.
- 4:36 — **HONEST ABOUT WHAT’S UNKNOWN**: No forecast invented for a distant event.
- 4:48 — **COMPARE YOUR OPTIONS**: Two alternatives for the iconic search.
- 4:57 — **THE PICK**: We do the homework. You make the memories.
- 5:06 — **ABOUT THIS DEMO**: Real app and AI · illustrative event listings.

## Re-record

1. Start the frontend, backend and Ollama.
2. From the root, run `backend/.venv/bin/python scripts/prepare-demo-narration.py`.
3. From `frontend`, run `node scripts/record-full-demo.mjs`. Use `DEMO_REHEARSAL=1` for a short rehearsal saved separately.
4. From the root, run `backend/.venv/bin/python scripts/export-full-demo.py`.

Forecasts and source freshness can change; review the script before a future recording. Earlier demo versions are preserved.
