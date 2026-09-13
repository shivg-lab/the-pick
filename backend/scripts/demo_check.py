import asyncio
import json
from pathlib import Path
import httpx


async def main():
    report = []
    async with httpx.AsyncClient(timeout=600) as client:
        pre = (await client.get("http://localhost:8000/api/providers")).json()
        print("PREFLIGHT", json.dumps(pre), flush=True)
        assert pre["agent_ready"], "Ollama or embeddings are not ready"
        for preset, query in [
            (
                "family",
                "I am in San Jose with two children, have a total budget of $120, want something nearby and prefer vegetarian food options.",
            ),
            (
                "iconic",
                "I want the most exciting, iconic Bay Area sports experience. Budget and distance do not matter.",
            ),
        ]:
            r = await client.post(
                "http://localhost:8000/api/recommendations", json={"query": query, "preset": preset, "mode": "agent"}
            )
            r.raise_for_status()
            data = r.json()
            Path(f"../evals/{preset}-ollama-result.json").write_text(json.dumps(data, indent=2))
            summary = {
                "scenario": preset,
                "agent_active": data["agent_active"],
                "retrieval": data["retrieval_mode"],
                "latency_ms": data["processing_ms"],
                "tools": [a["tool"] for a in data["activity"] if a["tool"]],
                "ranking": [
                    (r["event"]["id"], r["score"]["opportunity_score"], r["score"]["evidence_confidence"])
                    for r in data["recommendations"]
                ],
                "warnings": data["warnings"],
            }
            report.append(summary)
            print(json.dumps(summary, indent=2), flush=True)
            assert data["agent_active"], "Ollama investigation fell back"
            assert len(data["recommendations"]) == 3, "Expected three qualifying events in a presentation preset"
            assert data["retrieval_mode"] == "embeddinggemma"
        assert report[0]["tools"] != report[1]["tools"], "Requests should trigger different investigation tools"
    Path("../evals/ollama-integration.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
