# Evaluation for judges

Evaluation date: September 12, 2026. These are observed development results, not a claim of production accuracy.

## Automated evidence

| Check | Observed result | Scope |
|---|---|---|
| Backend unit/integration tests | 56 passed | Constraints, score/reweighting, deterministic order, confidence, providers, RAG, policies, citations, API, malformed model output and bounded loops |
| Frontend unit tests | 6 passed | Venue timezone, missing-price display, safe citation links, requested-fit copy, budget basis and context selection |
| TypeScript | Passed | Full frontend type check |
| Production build | Passed | Next.js 16.3.5 using supported Webpack |
| Browser journeys | 12 passed; plus two real-agent redesign journeys | Search → featured pick → alternatives → inline guide → sources → persisted feedback; stale preferences, no-results, busy and outage states |
| Repeatable evaluation suite | 24/24 scenarios passed | 15 deterministic profiles plus 9 guardrail/failure cases |
| Hard-constraint satisfaction | 30/30 returned recommendations | Explicit structured constraints within this small fixture suite |
| Citation metadata completeness | 100% | Every emitted citation has source ID, URL and retrieval time |
| Venue metadata relevance | 100% | Retrieved operational/context evidence matches the selected venue |
| Reranking consistency | 100% | Identical stored intent/evidence produces identical ordering |

Raw machine-readable evidence: [scenario results](../evals/summary.json), [browser results](../evals/playwright-results.json), [real Ollama integration](../evals/ollama-integration.json). Full request responses are saved separately for family and iconic presets. Use the raw latest integration artifact for exact measured timings and tool plans.

## Genuine Ollama runs

Both contrasting requests were executed against the actual local `qwen3:8b` and `embeddinggemma` models, without external sports API credentials. The family request ranked the San Jose Giants first. The iconic request ranked the Big Game first, followed by the 49ers and SF Giants. Their tool sequences differed. The original API integration measured 25.2 seconds (family) and 19.7 seconds (iconic); newer browser timings are recorded separately in `evals/redesign-integration.json`. In the iconic run, a mistyped event ID was rejected; the agent corrected it in a subsequent tool call and completed the policy retrieval. The public trace retains that warning and recovery. These outcomes come from the common scoring engine; altering preferences or evidence can change them.

The backend integration script requires three results, an active agent, semantic retrieval and different tool sequences. It fails loudly if the request silently falls back. Earlier real tests exposed a schema grammar incompatibility and invented default intent fields; both were fixed before the passing runs. The source-quote extraction check and malformed-output tests now cover those failure boundaries.

## Baseline and interpretation

The baseline retained in API responses and evaluation artifacts sorts the original inventory by distance; the personalized shortlist first enforces hard constraints, then ranks by the six-factor Opportunity Score. The baseline includes excluded events so the difference is inspectable. This demonstrates a different decision procedure, not proven user preference lift.

The fixture suite achieved complete constraint satisfaction and metadata completeness. It does not prove event accuracy: the fixtures are deliberately illustrative. Venue metadata precision is not a human judgment of semantic relevance. Source IDs do not by themselves prove a source entails every claim. Explanations are extractive and source-bound by construction, but no independent human unsupported-claim audit was completed.

Fallback timings in the evaluation summary use an explicitly offline mock preflight and lexical development retrieval. They must not be advertised as Ollama latency. Real model timing is recorded in `ollama-integration.json` and varies with hardware and warm/cold loading.

## Next evaluation

Recruit families, travelers and newcomers to compare a date/distance baseline with the personalized shortlist on the same verified inventory. Randomize ordering. Collect chosen event, willingness to attend, reason, source usefulness and any incorrect claim. Separately annotate source entailment and RAG relevance. Report uncertainty and sample size; do not tune weights on a handful of feedback entries.

No credentialed Ticketmaster/Sportradar test, clean-machine dependency installation, Docker build or human preference study is claimed. Lockfiles, setup instructions and the native local tests provide the reproducibility path.


## Recommendation-led UI verification

The redesigned UI retains the same backend ranking and baseline data. `evals/redesign-integration.json` records real family and iconic agent runs, each with one featured pick and two alternatives. Layouts were inspected at 360, 390, 768, 900, 1024 and 1440 CSS pixels. Checks include no horizontal overflow, guide keyboard focus containment and restoration, and read-only request inputs during inference.

Frontend unit checks cover per-ticket versus total-budget wording and ensure unrestricted iconic requests lead with supplied historical context rather than irrelevant cost/distance claims. The visible comparison section was removed; baseline evaluation remains available in existing backend evaluation artifacts.

## Visitor preparation extension

Parking, seating convenience and attire additions passed 71 backend tests, 6 frontend tests, the production build, and all 12 desktop/mobile browser journeys. Checks cover exact venue/event/sport boundaries, missing information, outdated-season guidance, 90-day freshness, stored-response compatibility, source inclusion, and the bounded guide tool call. Browser journeys open the new tab directly from the winner preview and check source age, seating facts, comfort labels and overflow.

## Weather-informed attire

The weather extension passed the existing backend suite plus 13 focused cases for caching without redating, exact venue coordinates, UTC windows across local midnight, past/distant-event rejection, provider failures, missing hourly coverage, unit validation, malformed/non-finite values, unknown precipitation, and condition-based attire with scoped venue restrictions. Six frontend tests, the production build and all 12 desktop/mobile browser journeys also passed. `evals/weather-live.json` records a successful real Open-Meteo lookup for the San Jose demo date. The real-agent verification checks both an available family-outing forecast and an out-of-window November event.
