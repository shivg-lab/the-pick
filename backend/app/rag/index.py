import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
from app.models.domain import EvidenceItem, EventCandidate
from app.providers.llm import EmbeddingProvider, ProviderError

ALLOWED_HOSTS = {
    "mlb.com",
    "www.mlb.com",
    "www.milb.com",
    "milb.com",
    "levisstadium.com",
    "www.levisstadium.com",
    "gostanford.com",
    "calbears.com",
    "sjsuspartans.com",
    "bayfc.com",
    "www.49ers.com",
}


def tokens(text: str) -> set[str]:
    stop = {"the", "and", "at", "for", "a", "an", "of", "in", "to", "is", "are", "with", "your", "this"}
    return set(re.findall(r"[a-z0-9]+", text.lower())) - stop


class LexicalEmbeddingProvider:
    model = "lexical-hash-v1"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        result = []
        for text in texts:
            v = [0.0] * 512
            for token in tokens(text):
                i = int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % 512
                v[i] += 1
            result.append(v)
        return result


class LocalVectorIndex:
    """Small, persisted cosine index. Model + corpus fingerprints prohibit embedding mixing."""

    def __init__(self, corpus_path: Path, index_path: Path):
        self.corpus_path, self.index_path = corpus_path, index_path
        self.documents = json.loads(corpus_path.read_text())
        self.chunks = []
        for d in self.documents:
            if urlparse(d["source_url"]).hostname not in ALLOWED_HOSTS:
                raise ValueError("Knowledge source is not allowlisted")
            words = d["text"].split()
            for n, offset in enumerate(range(0, len(words), 150)):
                chunk = {**d, "chunk_id": f"{d['id']}:{n}", "text": " ".join(words[offset : offset + 180])}
                self.chunks.append(chunk)
        self.fingerprint = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
        self.vectors: np.ndarray | None = None
        self.model: str | None = None
        if index_path.exists():
            try:
                saved = json.loads(index_path.read_text())
                if saved["fingerprint"] == self.fingerprint and len(saved["vectors"]) == len(self.chunks):
                    self.vectors = np.asarray(saved["vectors"], dtype=float)
                    self.model = saved["model"]
            except (ValueError, KeyError):
                pass

    def ready(self, model: str) -> bool:
        return self.model == model and self.vectors is not None

    async def ingest(self, provider: EmbeddingProvider):
        if self.ready(provider.model):
            return
        vectors = []
        for i in range(0, len(self.chunks), 12):
            vectors.extend(await provider.embed([f"{d['title']}. {d['text']}" for d in self.chunks[i : i + 12]]))
        arr = np.asarray(vectors, dtype=float)
        if not np.isfinite(arr).all() or np.any(np.linalg.norm(arr, axis=1) == 0):
            raise ProviderError("Embedding index validation failed")
        self.model, self.vectors = provider.model, arr
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.index_path.with_suffix(".tmp")
        temporary.write_text(json.dumps({"model": self.model, "fingerprint": self.fingerprint, "vectors": vectors}))
        temporary.replace(self.index_path)

    def evidence(self, d: dict, score: float) -> EvidenceItem:
        retrieved = datetime.fromisoformat(d["ingestion_date"])
        age = (datetime.now(timezone.utc) - retrieved).days
        historical = d["category"] == "context" and bool(d.get("effective_date"))
        stale = not historical and (
            d.get("needs_recheck", False)
            or age
            > (
                90
                if d["category"] in {"policy", "food", "accessibility", "arrival", "parking", "seating", "attire"}
                else 365
            )
        )
        return EvidenceItem(
            id=d["chunk_id"],
            claim=d["text"],
            category=d["category"],
            source_id=d["id"],
            source_title=d["title"],
            source_url=d["source_url"],
            authority=d["authority"],
            retrieved_at=retrieved,
            effective_date=d.get("effective_date"),
            freshness="historical" if historical else "stale" if stale else "current",
            confidence=0.95 if not stale else 0.55,
            retrieval_score=round(score, 4),
            venue=d["venue"],
            event_id=d.get("event_id"),
            event_type=d.get("event_type"),
            field=d.get("field"),
            value=d.get("value"),
        )

    def visitor_evidence(self, event: EventCandidate) -> list[EvidenceItem]:
        """Exact metadata lookup for practical guide facts, independent of semantic ranking."""
        return [
            self.evidence(d, 1.0)
            for d in self.chunks
            if d["category"] in {"parking", "seating", "attire"}
            and d["venue"] == event.venue
            and (not d.get("event_id") or d["event_id"] == event.id)
            and (not d.get("event_type") or d["event_type"] == event.sport)
        ]

    async def retrieve(
        self, query: str, provider: EmbeddingProvider, event: EventCandidate, categories: list[str], limit: int = 12
    ) -> list[EvidenceItem]:
        if not self.ready(provider.model):
            raise ProviderError("Vector index not ready for the configured embedding model")
        vector = np.asarray((await provider.embed([query]))[0])
        denominator = np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(vector)
        similarities = self.vectors @ vector / np.maximum(denominator, 1e-10)
        candidates = []
        for i, d in enumerate(self.chunks):
            # Exact venue/event metadata gates prevent semantically similar policies crossing venues.
            if d["venue"] != event.venue or d["category"] not in categories:
                continue
            if d.get("event_id") and d["event_id"] != event.id:
                continue
            if d.get("event_type") and d["event_type"] != event.sport:
                continue
            # Context must overlap the question; operational facts use exact category+venue gating.
            if d["category"] == "context" and not tokens(query) & tokens(d["text"] + " " + d["title"]):
                continue
            candidates.append((float(similarities[i]), d))
        candidates.sort(key=lambda x: (-x[0], x[1]["chunk_id"]))
        return [self.evidence(d, s) for s, d in candidates[: min(limit, 16)]]
