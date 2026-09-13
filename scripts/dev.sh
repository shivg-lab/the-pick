#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v node >/dev/null 2>&1; then
  for runtime_bin in "$ROOT"/.runtime/node-*/bin; do
    if [[ -x "$runtime_bin/node" ]]; then export PATH="$runtime_bin:$PATH"; break; fi
  done
fi
command -v node >/dev/null || { echo 'Install Node.js 24 LTS first.'; exit 1; }
[[ -x "$ROOT/backend/.venv/bin/python" ]] || { echo 'Run: cd backend && uv sync'; exit 1; }
[[ -d "$ROOT/frontend/node_modules" ]] || { echo 'Run: cd frontend && npm ci'; exit 1; }
cd "$ROOT/backend"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM
cd "$ROOT/frontend"
npm run dev
