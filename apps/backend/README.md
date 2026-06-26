# RAG Studio Pro — Backend

FastAPI service (Python 3.12, managed with [uv](https://docs.astral.sh/uv/)).

## Run via Docker (recommended)

From the repo root:

```bash
docker compose up backend
```

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs · Health: http://localhost:8000/health

## Layout

```
app/
  main.py              FastAPI app factory + router wiring
  core/config.py       Settings (env-driven, pydantic-settings)
  api/v1/router.py     Versioned API router (/api/v1)
  api/v1/endpoints/    Endpoint modules (health, ...)
  worker/celery_app.py Celery app (Redis broker)
```

Endpoints are versioned under `/api/v1`. The unversioned `/health` is kept
stable for container/load-balancer probes.
