# RAG Studio Pro backend — FastAPI on Python 3.12, managed with uv.
FROM python:3.12-slim

# uv binaries
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Keep the virtualenv outside /app so a bind-mount of the source
    # in development does not shadow installed dependencies.
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --no-install-project

# Application source.
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
