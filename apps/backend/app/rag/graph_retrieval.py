"""Graph retrieval: query entities -> seed match -> multi-hop subgraph traversal."""

import uuid

from starlette.concurrency import run_in_threadpool

from app.rag import graph_extraction, graph_store


async def retrieve(kb_id: uuid.UUID, query: str) -> tuple[list[dict], list[str]]:
    """Return (relationship triples, seed terms) relevant to the query."""
    terms = await graph_extraction.extract_query_entities(query)
    if not terms:
        # Fallback: use the longer words from the query as match terms.
        terms = [w for w in query.split() if len(w) > 3]
    triples = await run_in_threadpool(graph_store.query_subgraph, str(kb_id), terms)
    return triples, terms
