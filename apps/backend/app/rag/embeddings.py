"""Embedding providers.

Local models (MiniLM, BGE) run via fastembed (ONNX — no torch). Gemini
embeddings use the Generative Language REST API. All functions are synchronous;
async callers wrap them in a threadpool.
"""

from functools import lru_cache

import httpx

from app.core.config import settings

# model key -> (backend, model name, vector dimension)
EMBEDDING_MODELS: dict[str, dict] = {
    "minilm": {
        "backend": "fastembed",
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "dim": 384,
    },
    "bge": {"backend": "fastembed", "name": "BAAI/bge-small-en-v1.5", "dim": 384},
    "gemini": {"backend": "gemini", "name": "text-embedding-004", "dim": 768},
}
DEFAULT_MODEL = "minilm"

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"


def _config(model_key: str) -> dict:
    return EMBEDDING_MODELS.get(model_key, EMBEDDING_MODELS[DEFAULT_MODEL])


def get_dimensions(model_key: str) -> int:
    return _config(model_key)["dim"]


@lru_cache(maxsize=4)
def _fastembed(name: str):
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=name, cache_dir=settings.fastembed_cache_dir)


def _embed_fastembed(name: str, texts: list[str]) -> list[list[float]]:
    return [[float(x) for x in vec] for vec in _fastembed(name).embed(texts)]


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    if not settings.gemini_api_key:
        raise RuntimeError("Gemini embeddings selected but GEMINI_API_KEY is not set.")
    model = settings.gemini_embedding_model
    url = GEMINI_EMBED_URL.format(model=model)
    out: list[list[float]] = []
    with httpx.Client(timeout=30) as client:
        for text in texts:
            resp = client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={"model": f"models/{model}", "content": {"parts": [{"text": text}]}},
            )
            resp.raise_for_status()
            out.append(resp.json()["embedding"]["values"])
    return out


def embed_texts(model_key: str, texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    cfg = _config(model_key)
    if cfg["backend"] == "gemini":
        return _embed_gemini(texts)
    return _embed_fastembed(cfg["name"], texts)


def embed_query(model_key: str, query: str) -> list[float]:
    return embed_texts(model_key, [query])[0]
