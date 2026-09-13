# Recommendation-led redesign

The page now gives the top recommendation clear visual priority while retaining the cream background, orange highlights, dark green accents, original stadium artwork and product copy.

## Experience

1. Start with the natural-language request or the family/iconic presets.
2. Refine the outing in the desktop sidebar; on mobile, expand **Your preferences**. Dates, sports, accessibility and model mode sit under **Dates, sports & more**.
3. Follow completed agent activity while inputs are locked for the running request.
4. Review the full-width **THE PICK FOR YOU** card. Fit wording uses actual budget and radius constraints; iconic requests lead with supplied context. Scores and costs remain backend values.
5. Preview bags, outside food, food options and arrival inline. Missing data, stale source labels and conflicts remain visible. Open the full guide for details, citations and feedback.
6. Compare the two smaller alternatives below the winner.
7. End with **We do the homework. You make the memories.**

After a search the introduction becomes compact. Editing a request, preset, filter or model mode displays a stale-results notice until a new result is returned. The distance-sort comparison was removed from the page; the backend baseline and evaluation artifacts remain intact.

## Implementation boundaries

- `frontend/components/Preferences.tsx`: responsive preferences and existing filter contracts.
- `frontend/components/ResultViews.tsx`: featured winner, alternatives, inline guide and detailed guide.
- `frontend/lib/presentation.ts`: evidence-based fit wording that respects budget basis and requested constraints.
- `frontend/app/page.tsx`: request lifecycle, compact introduction, result freshness and layout.
- `frontend/app/globals.css`: responsive layout and palette.

No changes to backend ranking weights, eligibility, model providers, APIs, source corpus or feedback storage were required. Inline preparation content comes from the returned guide, not from the earlier HTML prototype's fixtures.

## Verification and demo

Production build and frontend unit checks pass. Twelve desktop/mobile browser checks cover the complete fallback journey, feedback, empty results, unavailable backend, missing model setup, stale preferences and busy responses. Real Ollama journeys verify the family and iconic scenarios with active semantic retrieval, two alternatives, responsive widths and keyboard focus handling. See `evals/redesign-integration.json` and `docs/screenshots/redesign/`.

The updated captioned MP4 is in `docs/demo-video-v2/`; the original video remains in `docs/demo-video/`. The recording uses actual local inference, with the waiting period shortened and labeled.
