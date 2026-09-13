# Deployment notes

## Primary: local presentation

Native Ollama on the host gives the simplest GPU path. Use `./scripts/dev.sh` or run the backend and frontend separately. For a stable production UI, build with `npm run build`, then serve using `npm start`. Run preflight and both preset integrations before presenting; keep the agent-ready header visible.

Native development and production builds were exercised. Docker files are supplied, but a full Docker image build and containerized Ollama connectivity were **not validated** in this environment.

## Optional Docker

With Docker running and Ollama available to the containers:

```bash
docker compose build
docker compose run --rm backend python -m scripts.ingest
docker compose up
```

The Compose file mounts backend data for persistent index/SQLite state and uses `host.docker.internal` for host Ollama. On Linux or a host restricted to loopback, that endpoint may not be reachable from a container; configure an appropriate host binding and firewall before using Docker. Do not expose Ollama to an untrusted network. Ports are bound to the local machine for this prototype.

The frontend Docker build uses `http://localhost:8000` as its browser API URL. Override its build argument for a remote deployment; a Docker service name is not a browser-accessible host. Set `CORS_ORIGINS` accordingly.

## Before public hosting

This project intentionally omits auth and multi-tenant isolation. Internet deployment needs access controls, per-user rate limits, data-retention/deletion rules, HTTPS, secret management and a production database migration. Do not expose the request/feedback API as a shared public service without those changes. No cloud deployment was performed.
