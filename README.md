# RAG Studio Pro

> Advanced Multi-Modal Intelligent RAG Platform with Hybrid Retrieval and Agentic Reasoning.

A production-oriented RAG platform that unifies **Vector RAG**, **Graph RAG**,
**Hybrid retrieval**, and **agentic orchestration** into one system — both an
experimentation studio for AI/ML engineers and a deployable enterprise
knowledge assistant.

## Status

**Phase 0 — Project Foundation & Development Infrastructure.** ✅

The project is built in strict dependency-ordered phases (see
[Implementation Plan](#roadmap)). This phase delivers the monorepo scaffold and
a one-command local stack.

## Quick start

Requires **Docker** + **Docker Compose**.

```bash
make up          # creates .env from .env.example, then docker compose up
# or:
cp .env.example .env
docker compose up --build
```

Then:

| Service        | URL                              |
| -------------- | -------------------------------- |
| Frontend       | http://localhost:3000            |
| Backend (API)  | http://localhost:8000            |
| API docs       | http://localhost:8000/docs       |
| Health probe   | http://localhost:8000/health     |
| Qdrant         | http://localhost:6333/dashboard  |
| Neo4j Browser  | http://localhost:7474            |
| MinIO Console  | http://localhost:9001            |

## Architecture

| Layer        | Technology                                                        |
| ------------ | ----------------------------------------------------------------- |
| Frontend     | Next.js (App Router), TypeScript, Tailwind v4, shadcn/ui          |
| Backend      | FastAPI, Python 3.12 (managed with `uv`)                          |
| Auth         | Clerk → JWT → FastAPI (RBAC)                                       |
| Relational   | PostgreSQL                                                        |
| Vectors      | Qdrant (one collection per knowledge base)                        |
| Graph        | Neo4j                                                             |
| Object store | MinIO (S3-compatible)                                             |
| Cache/Queue  | Redis + Celery                                                    |
| RAG / Agent  | LangChain + LangGraph; Gemini / Groq / Claude / Ollama            |

Storage boundaries are strict and intentional — see each service's role in
`docker-compose.yml`.

## Repository layout

```
.
├── apps/
│   ├── frontend/        Next.js application
│   └── backend/         FastAPI application + Celery worker
├── packages/            Shared packages (added as needed)
├── docker-compose.yml   Local dev stack (one command)
├── Makefile             Developer convenience commands (`make help`)
└── .env.example         Environment template
```

## Roadmap

Build proceeds phase by phase; each phase has acceptance criteria that gate the
next:

0. **Foundation & Dev Infrastructure** ← _you are here_
1. Core Backend + Auth + Database
2. Knowledge Base + Storage + Ingestion Pipeline
3. Vector RAG
4. Chat Assistant
5. Graph RAG
6. Hybrid RAG + Studio
7. Agentic System
8. Production Hardening & Observability

## Development

```bash
make help        # list commands
make up          # start the stack
make down        # stop the stack
make logs        # tail logs
make health      # curl the backend health endpoint
make clean       # stop + remove volumes (destructive)
```

Pre-commit hooks (ruff for backend, prettier for frontend):

```bash
pipx install pre-commit && pre-commit install
```
