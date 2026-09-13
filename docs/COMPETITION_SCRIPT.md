# Four-minute competition script

## Before the room fills

Start Ollama and both app servers. Run `python -m scripts.preflight` and `python -m scripts.demo_check` from the backend environment. Keep the browser at localhost:3000. Avoid concurrent inference. Close memory-heavy apps. Confirm **Local agent ready** and that the latest corpus is indexed. Do not use fallback as the agent demonstration.

## 0:00–0:30 — The problem

“Event sites can tell a family what’s happening. They leave the harder work to the family: what fits our time and budget, whether the kids will enjoy it, what bag we can carry, and whether we’ll find suitable food. The Pick connects Discover, Decide and Prepare.”

Point to the landing page. “This prototype compares eight deliberately illustrative seasonal scenarios. These are not live fixtures or real ticket prices. The venue and history evidence is separately sourced from official pages.”

## 0:30–1:30 — A family day

Choose **Family day, on a budget**. Click **Find my pick**.

“Everything runs locally through Ollama. The model extracts preferences with supporting quotes, chooses relevant tools, reads their results and can ask for missing evidence. This activity is actual completed work—not a simulated loading animation.”

While it runs, explain the hard limits: two adults and two children, $120 total outing budget, nearby and vegetarian preference. If the run is slow, explain the scoring separation while waiting.

“Here, the San Jose Giants scenario fits better than the biggest event. The winner is not hard-coded; all candidates use the same deterministic engine. There is no hidden-gem bonus.”

## 1:30–2:15 — Why trust the answer?

Point to the large “THE PICK FOR YOU” card, then the two smaller alternatives. Open the score breakdown. “Opportunity Score measures fit. Evidence Confidence measures how much trustworthy information supports the answer. Missing data is not turned into a fake neutral score.”

Show the inline **Know before you go** preview: bags, outside food, food options and arrival. Point out the clutch-size conflict. Open **Full venue guide**, show source dates, then switch to food.

“We did not assume pizza means verified vegetarian food. The guide says what is known, what is missing and what needs confirmation. If vegetarian food is a strict requirement, this event can be excluded.”

## 2:15–3:15 — Change the person, change the pick

Close the guide. Choose **The iconic Bay Area experience** and search again.

“Now price and distance don’t matter. The agent has a different research question: cultural significance, rivalry and atmosphere. You can see a different tool sequence. The Big Game, 49ers and major-league baseball rise naturally under the same algorithm.”

Open sources for the Big Game. “Historical RAG explains why a rivalry matters. Event APIs establish the schedule. We never use a history document as a live fixture or ticket-price source.”

## 3:15–4:00 — The engineering story

“The backend enforces eligibility, budgets, distance, source precedence, scoring and iteration limits. The model can decide what to investigate, but it cannot alter scores or invent new claims in the explanation. Explanations select from validated supplied sources. A local SQLite store preserves recommendations and feedback.”

“Automated tests cover the important failure paths, and repeatable scenarios compare constraints and citations. We have not yet claimed human preference lift over the baseline. That is the next evaluation.”

End at the closing section: “We do the homework. You make the memories.”

The distance-sort baseline remains in the API and evaluation artifacts for technical discussion; it is no longer a section in the user experience.

## If something fails

Be candid. Open provider status, identify the missing model/index or busy request, and retry after resolving it. If fallback is necessary, call it non-agent resilience and use the stored integration report to discuss what was previously tested. Do not relabel saved results as live work.


## Short shareable walkthrough

The redesigned recording lives in `docs/demo-video-v2/the-pick-demo.mp4`. The previous recording remains in `docs/demo-video/`.

The short walkthrough covers the request and preferences, the featured winner, score transparency, two smaller alternatives, inline preparation details, official sources, and the closing promise. Captions are included; there is no audio. The live local agent waiting period is shortened and labeled. Run `node scripts/record-demo.mjs` from `frontend/`, then `backend/.venv/bin/python scripts/export-demo.py` from the project root to recreate it.
