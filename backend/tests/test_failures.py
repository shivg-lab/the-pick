from unittest.mock import AsyncMock
import httpx
import pytest
from pydantic import ValidationError
from app.agents.intent import IntentExtraction, parse_intent
from app.agents.orchestrator import Concierge
from app.models.domain import SearchRequest, UserIntent
from app.providers.events import DemoEventProvider
from app.providers.llm import OllamaLLMProvider, ProviderError, ollama_schema
from app.providers.sports import DemoSportsProvider
from app.rag.index import LexicalEmbeddingProvider
from tests.test_api_agent import FakeLLM, OfflineLLM


async def test_event_provider_failure_is_safe(config, monkeypatch):
    monkeypatch.setattr(DemoEventProvider, "search", AsyncMock(side_effect=ProviderError("Event feed unavailable")))
    result = await Concierge(config, OfflineLLM()).recommend(SearchRequest(query="A local outing"))
    assert not result.recommendations
    assert any("Event feed unavailable" in w for w in result.warnings)


async def test_sports_provider_failure_does_not_invent_records(config, monkeypatch):
    config.app_mode = "demo"
    service = Concierge(config, FakeLLM(iconic=True))
    service.embedding = LexicalEmbeddingProvider()
    await service.index.ingest(service.embedding)
    monkeypatch.setattr(DemoSportsProvider, "get", AsyncMock(side_effect=ProviderError("Sports feed unavailable")))
    result = await service.recommend(SearchRequest(query="Iconic experience"))
    assert result.agent_active and result.recommendations
    assert any("Sports feed unavailable" in w for w in result.warnings)
    assert not any(c.category == "sports" for r in result.recommendations for c in r.citations)


async def test_hallucinated_intent_quote_is_rejected():
    fake = FakeLLM()
    fake.structured = AsyncMock(
        return_value=IntentExtraction.model_validate(
            {"changes": [{"field": "accessibility", "value": ["wheelchair"], "quote": "I need a wheelchair"}]}
        )
    )
    with pytest.raises(ProviderError):
        await parse_intent(SearchRequest(query="A fun game"), fake)


async def test_schema_compatibility_retains_python_constraints(config, monkeypatch):
    schema = ollama_schema(UserIntent.model_json_schema())
    assert schema["required"] == list(schema["properties"])
    assert "maximum" not in str(schema)
    with pytest.raises(ValidationError):
        UserIntent(budget=-1)
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"message": {"content": "{invalid"}})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        "app.providers.llm.httpx.AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    with pytest.raises(ProviderError, match="invalid structured"):
        await OllamaLLMProvider(config).structured("test", {}, UserIntent)
    assert len(calls) == 2


async def test_agent_max_iterations(config):
    config.app_mode = "demo"
    config.agent_max_steps = 1
    llm = FakeLLM(iconic=True)
    service = Concierge(config, llm)
    service.embedding = LexicalEmbeddingProvider()
    await service.index.ingest(service.embedding)
    result = await service.recommend(SearchRequest(query="Iconic experience"))
    assert llm.plans == 1
    assert result.provider_status["tool_calls"] <= config.agent_max_tool_calls


async def test_failed_or_absent_index_never_claims_agent(config):
    config.app_mode = "demo"
    result = await Concierge(config, FakeLLM()).recommend(SearchRequest(query="Family outing", preset="family"))
    assert not result.agent_active
    assert result.retrieval_mode == "lexical-hash-v1"


async def test_budget_value_must_match_quoted_dollars():
    fake = FakeLLM()
    fake.structured = AsyncMock(
        return_value=IntentExtraction.model_validate({"changes": [{"field": "budget", "value": 1200, "quote": "$120"}]})
    )
    with pytest.raises(ProviderError, match="quoted amount"):
        await parse_intent(SearchRequest(query="My total budget is $120"), fake)


async def test_wrong_location_type_is_a_validation_error():
    fake = FakeLLM()
    fake.structured = AsyncMock(
        return_value=IntentExtraction.model_validate(
            {"changes": [{"field": "location", "value": 42, "quote": "San Jose"}]}
        )
    )
    with pytest.raises(ValidationError):
        await parse_intent(SearchRequest(query="An outing in San Jose"), fake)
