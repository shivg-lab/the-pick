# Troubleshooting

| Symptom | Action |
|---|---|
| Backend unavailable in header | Start FastAPI on port 8000; inspect `/health`. |
| Model unreachable | Run `ollama serve`; if it says address already in use, the service is already running. |
| Chat or embedding model missing | Pull the exact configured tags: `qwen3:8b` and `embeddinggemma`. |
| Vector not ready | In `backend/`, run `uv run python -m scripts.ingest`; restart the backend after changing the corpus. |
| Models installed, still fallback | Run `uv run python -m scripts.preflight`; inspect warnings. Missing index and malformed model output are distinct failure cases. |
| Slow first request | The model is loading into memory. Close memory-heavy apps and warm it with a preset before presenting. |
| Grammar-compiler failure | Use the shipped compatibility serializer. It omits unsupported wire bounds but keeps Pydantic validation. Do not replace validation with untyped JSON. |
| Ollama invents a preference | Extraction now requires a literal input quote. Review parsed intent; use an explicit form field to override an interpretation. |
| “No qualifying events” | Check date, radius, budget, sport/team, dietary-required and accessibility constraints. The seasonal sampler is not today’s real schedule. |
| Strict vegetarian request excludes the local park | The corpus lacks explicit vegetarian confirmation there. This is expected; a preference can retain the candidate with a warning, a requirement cannot. |
| Hybrid returns no events | Live listings need eligibility signals and curated enrichment. The real local feed is intentionally empty until reviewed fixtures are added. |
| 429 busy | One local model investigation runs at a time. Wait for completion before retrying. |
| Browser on another device cannot reach API | Build the frontend with the host’s LAN API URL and explicitly add that frontend origin to CORS. `localhost` on the phone refers to the phone. |
| Production CSS build fails under Turbopack | The supplied scripts use supported `--webpack`; keep it for the demo. |
| Dependency versions changed | Use `uv sync --frozen` and `npm ci` with the included lockfiles. |
| Feedback missing after restart | Check that the same `backend/data/the-pick.sqlite` file or Docker volume is in use. |

The resilience path is labeled **Fallback mode—agent reasoning is unavailable.** It supports navigation, presets, deterministic ranking, guides and feedback, but it must not be presented as a successful agent run.

Changing a public frontend environment variable requires restarting development or rebuilding production. Backend configuration reads the repository-root `.env`; frontend custom settings should be exported to the build process or placed in `frontend/.env.local`.

Do not paste API keys into bug reports. Structured logs omit provider keys, model payloads and raw user requests; local SQLite responses do retain requests as part of the prototype’s review history.
