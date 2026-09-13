# The Pick — silent demo

Share **the-pick-demo.mp4**: 3:27, 16.6 MB. H.264 video, 1440 × 1000, 25 fps. No audio track. On-screen chapter captions are included.

The family search includes the winner, alternatives, score breakdown and full venue guide: bags, food, arrival, parking, seating, weather, attire, sources and feedback. The iconic search shows the changed winner, reasons and alternatives without repeating the guide.

Both searches use the real local app and Ollama agent. Only long AI waits are shortened. The app's event fixtures and source labels remain unchanged. Previous recordings are preserved.

## Optional voiceover

Use `voiceover-script.md` for chapter timing and `voiceover-script.txt` for clean copy. These files are suggestions for adding a voiceover later; no speech was generated for this version. `the-pick-demo.srt` contains the on-screen captions, not a spoken transcript.

## Chapters

- 0:00 — THE PICK
- 0:09 — FAMILY ON A BUDGET
- 0:17 — MAKE IT YOUR DAY
- 0:24 — THE LOCAL AGENT
- 0:32 — YOUR FAMILY PICK
- 0:42 — THE EVENT, AT A GLANCE
- 0:50 — SHOW YOUR WORK
- 0:58 — ALSO WORTH SHOWING UP FOR
- 1:05 — KNOW BEFORE YOU GO
- 1:12 — THE FULL VENUE GUIDE
- 1:22 — PACK WITH CONFIDENCE
- 1:30 — FOOD & ARRIVAL
- 1:38 — GETTING THERE
- 1:46 — PARKING & COMFORT
- 1:55 — FIND A COMFORTABLE SEAT
- 2:03 — WEATHER FOR YOUR OUTING
- 2:13 — WHAT TO WEAR
- 2:24 — THE EVIDENCE BEHIND THE GUIDE
- 2:30 — HELP IMPROVE THE NEXT PICK
- 2:38 — THE ICONIC EXPERIENCE
- 2:47 — A DIFFERENT INVESTIGATION
- 2:54 — YOUR ICONIC PICK
- 3:04 — UNDERSTAND THE TRADEOFFS
- 3:11 — COMPARE YOUR OPTIONS
- 3:19 — THE PICK

## Re-record

1. Start the frontend, backend and Ollama.
2. From `frontend`, run `node scripts/record-silent-demo.mjs`.
3. From the root, run `backend/.venv/bin/python scripts/export-silent-demo.py`.
