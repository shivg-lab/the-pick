import argparse
import asyncio
from app.core.config import settings
from app.providers.llm import OllamaEmbeddingProvider
from app.rag.index import LexicalEmbeddingProvider, LocalVectorIndex


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lexical", action="store_true", help="Development fallback only; does not satisfy agent preflight"
    )
    args = parser.parse_args()
    provider = LexicalEmbeddingProvider() if args.lexical else OllamaEmbeddingProvider(settings)
    index = LocalVectorIndex(
        settings.data_dir / "knowledge/corpus.json",
        settings.data_dir / ("knowledge/lexical-index.json" if args.lexical else "knowledge/index.json"),
    )
    await index.ingest(provider)
    print(f"Indexed {len(index.chunks)} chunks with {index.model}.")


if __name__ == "__main__":
    asyncio.run(main())
