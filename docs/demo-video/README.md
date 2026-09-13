# The Pick demo video

Share `the-pick-demo.mp4`. H.264 MP4, 1440 × 1000, 25 fps, with on-screen captions and no audio.

Recorded from the running local application using its real Ollama agent. The middle of the AI waiting period is cut for pacing; all other interactions play at normal speed. Event scenarios, dates and prices are illustrative, not live listings. Venue guidance comes from the app’s stored sources.

## Walkthrough

- 0:01 — THE PICK: Your personal Bay Area sports concierge. Discover. Decide. Prepare.
- 0:06 — 01 / DISCOVER: Start with a family day: four people, nearby, with a $120 total budget.
- 0:12 — LOCAL AI: Ollama investigates the request and supporting sources. Waiting time shortened.
- 0:23 — 02 / DECIDE: Three recommendations ranked for this outing, with a clear top pick.
- 0:29 — FIT + CONFIDENCE: Compare personal fit, evidence confidence, ticket prices and outing estimates.
- 0:36 — TRANSPARENT SCORING: Open the score breakdown to see the factors and their weights.
- 0:44 — A PERSONAL SHORTLIST: See how ranking by fit compares with an ordinary list sorted by distance.
- 0:51 — 03 / PREPARE: Check bags, food and water rules before heading to the venue.
- 0:58 — UNKNOWNS STAY VISIBLE: Conflicting official guidance is flagged so you know what to confirm.
- 1:02 — FOOD + ARRIVAL: Food preferences and arrival advice include clear information gaps.
- 1:09 — CHECK THE EVIDENCE: Source links and review dates make the venue guidance easy to inspect.
- 1:17 — THE PICK: Find your game. Understand the tradeoffs. Arrive prepared.
- 1:22 — ABOUT THIS DEMO: Recorded from the local app. Event dates and prices are illustrative, not live listings.

## Re-record

Start the frontend, backend and Ollama, then run `node scripts/record-demo.mjs` from `frontend/`. Run `backend/.venv/bin/python scripts/export-demo.py` from the repository root. The export script uses the project-local imageio-ffmpeg binary in `.runtime/video-tools/`.
