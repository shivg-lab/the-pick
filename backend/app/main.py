import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.agents.orchestrator import Concierge
from app.core.config import Settings, settings
from app.core.database import Repository
from app.models.domain import Feedback, RecommendationResponse, SearchRequest

logger = logging.getLogger("the_pick")
logging.basicConfig(level=logging.INFO, format="%(message)s")
# HTTP libraries may otherwise log provider URLs containing credentials.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def create_app(config: Settings = settings, concierge=None):
    service = concierge or Concierge(config)
    repo = Repository(config.data_dir / "the-pick.sqlite")
    jobs: dict[str, dict] = {}
    tasks = set()
    lock = asyncio.Semaphore(1)

    @asynccontextmanager
    async def lifespan(app):
        check = await service.preflight()
        logger.info(
            json.dumps(
                {"event": "preflight", "agent_ready": check["agent_ready"], "vector_ready": check["vector_ready"]}
            )
        )
        yield
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    app = FastAPI(title=config.app_name, version="0.1.0", lifespan=lifespan)
    app.state.concierge = service
    app.state.repository = repo
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins.split(","),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @app.middleware("http")
    async def request_metadata(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        if int(request.headers.get("content-length", "0") or 0) > 16384:
            return JSONResponse(status_code=413, content={"detail": "Request is too large"})
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        logger.info(
            json.dumps(
                {
                    "event": "http",
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000),
                }
            )
        )
        return response

    @app.exception_handler(Exception)
    async def safe_error(request, exc):
        logger.error(
            json.dumps(
                {
                    "event": "request_failed",
                    "request_id": getattr(request.state, "request_id", None),
                    "error_type": type(exc).__name__,
                }
            )
        )
        return JSONResponse(
            status_code=500, content={"detail": "Unable to complete the request. Please retry or use fallback mode."}
        )

    @app.get("/health")
    async def health():
        return {"status": "ok", "app": config.app_name, "preflight": await service.preflight()}

    @app.get("/api/providers")
    async def providers():
        return await service.preflight()

    @app.post("/api/recommendations", response_model=RecommendationResponse)
    async def recommendations(data: SearchRequest, request: Request):
        if lock.locked():
            raise HTTPException(429, "The local model is busy. Please retry shortly.")
        async with lock:
            try:
                result = await service.recommend(data, request_id=request.state.request_id)
            except ValidationError:
                raise HTTPException(422, "The interpreted request is invalid. Check your dates and filters.") from None
            repo.save(result)
            return result

    @app.get("/api/recommendations/{request_id}")
    async def stored(request_id: str):
        result = repo.get(request_id)
        if not result:
            raise HTTPException(404, "Recommendation not found")
        return result

    @app.post("/api/jobs", status_code=202)
    async def start_job(data: SearchRequest):
        # Queue depth is bounded to avoid runaway local inference and memory growth.
        if any(j["status"] in {"queued", "running"} for j in jobs.values()) or lock.locked():
            raise HTTPException(429, "The local model is working on another outing. Try again shortly.")
        if len(jobs) >= 100:
            for key in list(jobs)[:50]:
                if jobs[key]["status"] not in {"queued", "running"}:
                    del jobs[key]
        id = str(uuid.uuid4())
        jobs[id] = {"request_id": id, "status": "queued", "activity": []}

        async def work():
            async with lock:
                jobs[id]["status"] = "running"

                async def notify(activity):
                    jobs[id]["activity"].append(activity.model_dump())

                try:
                    result = await service.recommend(data, notify, id)
                    repo.save(result)
                    jobs[id].update(status="complete", result=result.model_dump(mode="json"))
                except Exception as exc:
                    logger.error(
                        json.dumps({"event": "job_failed", "request_id": id, "error_type": type(exc).__name__})
                    )
                    jobs[id].update(
                        status="failed",
                        error="Investigation could not finish. Check your filters and retry, or choose fallback mode.",
                    )

        task = asyncio.create_task(work())
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        return {"request_id": id}

    @app.get("/api/jobs/{request_id}")
    async def get_job(request_id: str):
        if request_id not in jobs:
            raise HTTPException(404, "Investigation not found")
        return jobs[request_id]

    @app.post("/api/feedback", status_code=201)
    async def feedback(data: Feedback):
        try:
            id = repo.feedback(data)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        return {"id": id, "saved": True}

    @app.get("/api/demo/fixtures/{event_id}")
    async def fixture(event_id: str):
        events = json.loads((config.data_dir / "demo/events.json").read_text())
        event = next((e for e in events if e["id"] == event_id), None)
        if not event:
            raise HTTPException(404, "Fixture not found")
        return {
            "notice": "Illustrative, authored scenario assumptions. Not a live or verified event listing.",
            "event": event,
        }

    return app


app = create_app()
