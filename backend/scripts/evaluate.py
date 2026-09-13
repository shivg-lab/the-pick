"""Repeatable development-only evaluation; no endpoint exposed in the product."""

import asyncio
import json
import statistics
import subprocess
import sys
import time
from app.agents.orchestrator import Concierge
from app.core.config import BACKEND, Settings
from app.models.domain import SearchRequest
from app.ranking.engine import hard_filters, need_filters, rank


class Offline:
    async def preflight(self):
        return {"reachable": False, "chat_installed": False, "embedding_installed": False}


async def main():
    root = BACKEND.parent
    scenarios = json.loads((root / "evals/scenarios.json").read_text())
    config = Settings(app_mode="fallback")
    service = Concierge(config, Offline())
    rows = []
    checks = 0
    violations = 0
    citation_total = 0
    citation_valid = 0
    relevance_total = 0
    relevance_valid = 0
    consistent = 0
    for case in scenarios:
        started = time.perf_counter()
        if "test" in case:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", case["test"]], cwd=BACKEND, capture_output=True, text=True
            )
            rows.append(
                {
                    "id": case["id"],
                    "passed": result.returncode == 0,
                    "kind": "guardrail test",
                    "duration_ms": round((time.perf_counter() - started) * 1000),
                    "detail": result.stdout[-1500:] if result.returncode else "Passed",
                }
            )
            continue
        result = await service.recommend(
            SearchRequest(query=case["query"], preset=case.get("preset"), filters=case["filters"], mode="fallback")
        )
        passed = True
        ids = [r.event.id for r in result.recommendations]
        if case.get("expected_top"):
            passed = bool(ids) and ids[0] == case["expected_top"]
        if case.get("expected_empty"):
            passed = not ids
        for rec in result.recommendations:
            checks += 1
            failures = hard_filters(rec.event, result.parsed_intent) + need_filters(result.parsed_intent, rec.citations)
            violations += bool(failures)
            for c in rec.citations:
                citation_total += 1
                citation_valid += bool(c.source_id and c.source_url and c.retrieved_at)
                if c.category not in {"fixture", "event", "sports"}:
                    relevance_total += 1
                    relevance_valid += c.venue == rec.event.venue
        rescored = rank(
            [r.event for r in result.recommendations],
            result.parsed_intent,
            {r.event.id: r.citations for r in result.recommendations},
        )
        consistent += ids == [e.id for e, s in rescored]
        rows.append(
            {
                "id": case["id"],
                "passed": passed,
                "kind": "deterministic fallback scenario",
                "duration_ms": result.processing_ms,
                "ranking": ids,
                "top_score": result.recommendations[0].score.opportunity_score if ids else None,
                "baseline_first": result.baseline[0]["event_id"] if result.baseline else None,
            }
        )
    summary = {
        "scenarios": len(rows),
        "passed": sum(r["passed"] for r in rows),
        "hard_constraint_satisfaction": (checks - violations) / checks if checks else None,
        "recommendations_checked": checks,
        "citation_metadata_completeness": citation_valid / citation_total if citation_total else None,
        "venue_metadata_relevance": relevance_valid / relevance_total if relevance_total else None,
        "reranking_consistency": consistent / 15,
        "median_fallback_latency_ms": statistics.median(
            r["duration_ms"] for r in rows if r["kind"].startswith("deterministic")
        ),
        "live_event_accuracy": "Not measured: fixtures are illustrative.",
        "semantic_relevance": "Venue metadata precision measured; human semantic relevance judgments not collected.",
        "unsupported_claim_rate": "Not human-audited. Explanations use exact supplied source claims; fixture assumptions are labeled.",
        "user_preference_vs_baseline": "Not measured: collect human feedback before claiming preference lift.",
        "rows": rows,
    }
    (root / "evals/summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0 if all(r["passed"] for r in rows) and not violations else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
