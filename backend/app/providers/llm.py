import asyncio
import json
from typing import Protocol, TypeVar
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import Settings

T = TypeVar("T", bound=BaseModel)


def ollama_schema(value):
    """Ollama's grammar compiler rejects some numeric bounds; Python still enforces them.

    Make every property explicit so the model cannot silently omit a hard budget.
    Nullable fields remain nullable. No validation constraint is removed from Pydantic.
    """
    if isinstance(value, list):
        return [ollama_schema(x) for x in value]
    if not isinstance(value, dict):
        return value
    skip = {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
        "format",
        "default",
        "title",
    }
    output = {k: ollama_schema(v) for k, v in value.items() if k not in skip}
    if output.get("type") == "object" and "properties" in output:
        output["required"] = list(output["properties"])
    return output


class ProviderError(Exception):
    """Safe public error: never retain API keys or raw provider response bodies."""


class LLMProvider(Protocol):
    async def structured(self, system: str, payload: dict, schema: type[T]) -> T: ...


class OllamaLLMProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def preflight(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=4) as client:
                response = await client.get(f"{self.settings.ollama_base_url}/api/tags")
                response.raise_for_status()
                names = [m["name"] for m in response.json().get("models", [])]

            def installed(n):
                return n in names or f"{n}:latest" in names

            return {
                "reachable": True,
                "chat_installed": installed(self.settings.ollama_chat_model),
                "embedding_installed": installed(self.settings.ollama_embedding_model),
            }
        except (httpx.HTTPError, ValueError, KeyError):
            return {"reachable": False, "chat_installed": False, "embedding_installed": False}

    async def structured(self, system: str, payload: dict, schema: type[T]) -> T:
        # All model output is constrained by JSON Schema and validated again in Python.
        wire_schema = ollama_schema(schema.model_json_schema())
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                    response = await client.post(
                        f"{self.settings.ollama_base_url}/api/chat",
                        json={
                            "model": self.settings.ollama_chat_model,
                            "stream": False,
                            "think": False,
                            "format": wire_schema,
                            "keep_alive": "15m",
                            "options": {
                                "temperature": self.settings.llm_temperature,
                                "num_ctx": 8192,
                                "num_predict": 1600,
                            },
                            "messages": [
                                {"role": "system", "content": system},
                                {
                                    "role": "user",
                                    "content": json.dumps({**payload, "output_schema": wire_schema}, default=str),
                                },
                            ],
                        },
                    )
                    response.raise_for_status()
                    return schema.model_validate_json(response.json()["message"]["content"])
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                raise ProviderError("Ollama is unavailable or exceeded its time limit") from exc
            except (httpx.HTTPError, ValidationError, ValueError, KeyError) as exc:
                if attempt:
                    raise ProviderError("Ollama returned invalid structured output") from exc
                await asyncio.sleep(0.15)
        raise ProviderError("Ollama output validation failed")


class TemplateFallbackProvider:
    label = "Fallback mode—agent reasoning is unavailable."

    def explanation(self, name: str, score: float, facts: list[str]) -> str:
        return f"{name} scores {score:.0f}/100 for these preferences. " + " ".join(facts[:2])


class EmbeddingProvider(Protocol):
    model: str

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class OllamaEmbeddingProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.ollama_embedding_model
        self.cache: dict[tuple[str, ...], list[list[float]]] = {}

    async def embed(self, texts: list[str]) -> list[list[float]]:
        key = tuple(texts)
        if key in self.cache:
            return self.cache[key]
        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/embed",
                    json={"model": self.model, "input": texts, "truncate": False, "keep_alive": "15m"},
                )
                response.raise_for_status()
                vectors = response.json()["embeddings"]
                if len(vectors) != len(texts) or not vectors or not vectors[0]:
                    raise ValueError("Invalid vectors")
                if len(self.cache) > 128:
                    self.cache.clear()
                self.cache[key] = vectors
                return vectors
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError("Embedding model unavailable") from exc
