from fastapi.testclient import TestClient
from app.agents.orchestrator import Concierge, GroundedExplanation
from app.agents.intent import IntentExtraction
from app.agents.tools import ToolPlan
from app.main import create_app
from app.models.domain import SearchRequest
from app.providers.llm import ProviderError
from app.rag.index import LexicalEmbeddingProvider


class OfflineLLM:
    async def preflight(self):
        return {"reachable": False, "chat_installed": False, "embedding_installed": False}


class FakeLLM:
    def __init__(self, iconic=False, malformed=False):
        self.plans = 0
        self.iconic = iconic
        self.malformed = malformed

    async def preflight(self):
        return {"reachable": True, "chat_installed": True, "embedding_installed": True}

    async def structured(self, system, payload, schema):
        if self.malformed:
            raise ProviderError("Malformed structured output")
        if schema == IntentExtraction:
            values = (
                {"atmosphere": "iconic"}
                if self.iconic
                else {
                    "budget": 120,
                    "radius_miles": 25,
                    "children": 2,
                    "family_friendly": True,
                    "atmosphere": "relaxed",
                    "dietary": ["vegetarian"],
                }
            )
            return IntentExtraction.model_validate(
                {"changes": [{"field": k, "value": v, "quote": payload["query"]} for k, v in values.items()]}
            )
        if schema == ToolPlan:
            self.plans += 1
            names = (
                ["retrieve_sports_context", "get_sports_data", "retrieve_venue_policy"]
                if self.iconic
                else ["retrieve_venue_policy", "retrieve_food_options", "retrieve_sports_context"]
            )
            if self.plans > len(names):
                return ToolPlan(sufficient=True)
            return ToolPlan.model_validate(
                {"calls": [{"name": names[self.plans - 1], "arguments": {"event_ids": [], "query": ""}}]}
            )
        if schema == GroundedExplanation:
            return GroundedExplanation(selections=[])
        raise AssertionError(schema)


async def test_fallback_full_vertical_slice(config):
    service = Concierge(config, OfflineLLM())
    result = await service.recommend(SearchRequest(query="Family outing", preset="family"))
    assert not result.agent_active
    assert result.recommendations[0].event.id == "sj-giants"
    assert any("Fallback mode" in w for w in result.warnings)
    assert result.recommendations[0].guide.policy.conflicts
    assert result.provider_status["tool_calls"] <= 10
    assert len(result.recommendations) == 3


async def test_different_agent_tool_plans(config):
    config.app_mode = "demo"
    calls = []
    for iconic in [False, True]:
        service = Concierge(config, FakeLLM(iconic))
        service.embedding = LexicalEmbeddingProvider()
        await service.index.ingest(service.embedding)
        result = await service.recommend(SearchRequest(query="Iconic" if iconic else "Family outing"))
        assert result.agent_active
        assert result.provider_status["tool_calls"] <= 10
        calls.append([a.tool for a in result.activity if a.tool])
    assert "retrieve_food_options" in calls[0] and "get_sports_data" in calls[1]
    assert calls[0] != calls[1]


async def test_malformed_model_degrades_honestly(config):
    config.app_mode = "demo"
    service = Concierge(config, FakeLLM(malformed=True))
    service.embedding = LexicalEmbeddingProvider()
    await service.index.ingest(service.embedding)
    result = await service.recommend(SearchRequest(query="Family outing", preset="family"))
    assert not result.agent_active and result.recommendations


async def test_no_results(config):
    service = Concierge(config, OfflineLLM())
    result = await service.recommend(SearchRequest(query="A free game", filters={"budget": 0, "radius_miles": 1}))
    assert not result.recommendations and len(result.exclusions) == 8


def test_api_persistence_feedback_cors_validation(config):
    with TestClient(create_app(config, Concierge(config, OfflineLLM()))) as client:
        assert client.get("/health").status_code == 200
        response = client.post("/api/recommendations", json={"query": "Family outing", "preset": "family"})
        assert response.status_code == 200, response.text
        result = response.json()
        id = result["request_id"]
        assert client.get("/api/recommendations/" + id).json() == result
        feedback = {
            "request_id": id,
            "event_id": result["recommendations"][0]["event"]["id"],
            "rating": "up",
            "would_attend": True,
        }
        assert client.post("/api/feedback", json=feedback).status_code == 201
        assert client.post("/api/feedback", json={**feedback, "event_id": "missing"}).status_code == 422
        assert client.post("/api/recommendations", json={"query": "foo", "filters": {"budget": -2}}).status_code == 422
        assert client.get("/api/recommendations/missing").status_code == 404
        allowed = client.options(
            "/api/recommendations", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
        )
        assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
        denied = client.options(
            "/api/recommendations", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"}
        )
        assert "access-control-allow-origin" not in denied.headers
