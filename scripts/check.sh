#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
uv run ruff check app tests scripts
uv run pytest -q
uv run python -m scripts.evaluate
cd "$ROOT/frontend"
npm test
npm run typecheck
npm run build
