"""Text chunking + token counting.

Two strategies (selectable per knowledge base):
- recursive: LangChain RecursiveCharacterTextSplitter (fast, structural)
- semantic: split at embedding-similarity drops between sentences (topic-aware)
"""

import re

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

_encoder = tiktoken.get_encoding("cl100k_base")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


def recursive_chunk(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    return [c for c in splitter.split_text(text) if c.strip()]


def semantic_chunk(text: str, embedding_model: str) -> list[str]:
    """Group sentences into chunks, splitting where consecutive-sentence
    embedding similarity drops (topic boundaries), capped at chunk_size."""
    import numpy as np

    from app.rag import embeddings

    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
    if len(sentences) <= 2:
        return recursive_chunk(text)

    vecs = np.array(embeddings.embed_texts(embedding_model, sentences))
    # Cosine distance between consecutive sentences.
    norms = np.linalg.norm(vecs, axis=1)
    dists = []
    for i in range(len(sentences) - 1):
        denom = norms[i] * norms[i + 1] or 1e-9
        dists.append(1 - float(np.dot(vecs[i], vecs[i + 1]) / denom))
    # Boundary where distance exceeds the 75th percentile (topic shift).
    threshold = float(np.percentile(dists, 75)) if dists else 1.0

    chunks: list[str] = []
    current = sentences[0]
    for i in range(1, len(sentences)):
        too_big = len(current) + len(sentences[i]) > settings.chunk_size
        boundary = dists[i - 1] > threshold
        if boundary or too_big:
            chunks.append(current)
            current = sentences[i]
        else:
            current += " " + sentences[i]
    if current.strip():
        chunks.append(current)
    return chunks


def chunk_text(
    text: str, strategy: str = "recursive", embedding_model: str = "minilm"
) -> list[str]:
    if strategy == "semantic":
        return semantic_chunk(text, embedding_model)
    return recursive_chunk(text)
