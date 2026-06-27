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


def build_chat_prompt(
    query: str, chunks: list[RetrievedChunk], history: list[tuple[str, str]] | None = None
) -> str:
    """Prompt with retrieved context plus recent conversation turns."""
    context = "\n\n".join(f"[{i + 1}] {c.text}" for i, c in enumerate(chunks))
    convo = ""
    if history:
        turns = "\n".join(f"{role}: {content}" for role, content in history)
        convo = f"Conversation so far:\n{turns}\n\n"
    return f"{convo}Context:\n{context}\n\nQuestion: {query}\n\nAnswer (with inline [n] citations):"


def build_citations(chunks: list[RetrievedChunk], names: dict[str, str]) -> list[dict]:
    """Citation payload for source cards (stored on the assistant message)."""
    return [
        {
            "index": i + 1,
            "document_id": c.document_id,
            "file_name": names.get(c.document_id, "unknown"),
            "score": round(c.score, 4),
            "snippet": c.text[:240],
        }
        for i, c in enumerate(chunks)
    ]


def confidence(chunks: list[RetrievedChunk]) -> float | None:
    """Heuristic confidence: mean of retrieval similarity scores."""
    if not chunks:
        return None
    return round(sum(c.score for c in chunks) / len(chunks), 4)


GRAPH_SYSTEM = (
    "You are a knowledge assistant. Answer the question using ONLY the provided knowledge-graph "
    "relationships. Reason over multi-hop connections (e.g. chains, ownership, dependencies). "
    "If the relationships don't contain the answer, say you don't have enough information."
)


def build_graph_prompt(query: str, triples: list[dict]) -> str:
    facts = "\n".join(
        f"- {t['source']} {t['relation'].replace('_', ' ').lower()} {t['target']}" for t in triples
    )
    return f"Knowledge graph relationships:\n{facts}\n\nQuestion: {query}\n\nAnswer:"


def build_hybrid_prompt(query: str, chunks: list, triples: list[dict]) -> str:
    """Combine fused vector chunks with graph relationships into one context."""
    context = "\n\n".join(f"[{i + 1}] {c.text}" for i, c in enumerate(chunks))
    graph_block = ""
    if triples:
        facts = "\n".join(
            f"- {t['source']} {t['relation'].replace('_', ' ').lower()} {t['target']}"
            for t in triples
        )
        graph_block = f"\n\nKnowledge graph relationships:\n{facts}"
    return (
        f"Context:\n{context}{graph_block}\n\nQuestion: {query}\n\n"
        "Answer (with inline [n] citations):"
    )


async def generate_answer(query: str, chunks: list[RetrievedChunk]) -> dict:
    """Return {'text', 'usage'}. Raises llm.LLMNotConfigured if no LLM key is set."""
    if not chunks:
        return {"text": "I couldn't find anything relevant in this knowledge base.", "usage": {}}
    return await llm.generate(build_prompt(query, chunks), SYSTEM_PROMPT)
