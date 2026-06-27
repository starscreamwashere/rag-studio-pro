"""Grounded answer generation from retrieved chunks."""

from app.integrations import llm
from app.rag.retrieval import RetrievedChunk

SYSTEM_PROMPT = (
    "You are a precise enterprise knowledge assistant. Answer the question using ONLY the "
    "provided context. Cite supporting sources inline as [n], where n is the source number. "
    "If the answer is not contained in the context, say you don't have enough information."
)


def build_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(f"[{i + 1}] {c.text}" for i, c in enumerate(chunks))
    return f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer (with inline [n] citations):"


async def generate_answer(query: str, chunks: list[RetrievedChunk]) -> dict:
    """Return {'text', 'usage'}. Raises llm.LLMNotConfigured if no LLM key is set."""
    if not chunks:
        return {"text": "I couldn't find anything relevant in this knowledge base.", "usage": {}}
    return await llm.generate(build_prompt(query, chunks), SYSTEM_PROMPT)
