"""LLM-based knowledge-graph extraction.

Extracts entities + relationships from chunk text (sync, used in the worker)
and key entities from a query (async, used at retrieval time). Parsing is
defensive — LLM JSON output is not always clean.
"""

import json

from app.integrations import llm

ENTITY_TYPES = ["Person", "Organization", "Product", "Concept", "Location", "Event", "Other"]

EXTRACTION_SYSTEM = (
    "You extract a knowledge graph from text. Return ONLY a JSON object with two keys:\n"
    '  "entities": list of {"name": str, "type": one of '
    f"{ENTITY_TYPES}}},\n"
    '  "relationships": list of {"source": str, "relation": str, "target": str}.\n'
    "Use entity names exactly as written. 'relation' is a short UPPER_SNAKE_CASE verb phrase "
    "(e.g. DEPENDS_ON, OWNED_BY, WORKS_FOR). source/target must be entity names from the list. "
    "If nothing is found, return empty lists. Output JSON only, no prose."
)

QUERY_ENTITIES_SYSTEM = (
    "Extract the key entity names from the user's question. "
    'Return ONLY a JSON array of strings, e.g. ["Acme", "billing system"]. '
    "If none, return []."
)


def _json_object(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}


def _json_array(text: str) -> list:
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []


def extract_graph(text: str) -> dict:
    """Return {'entities': [...], 'relationships': [...]} for a chunk (sync)."""
    raw = llm.generate_sync(text, EXTRACTION_SYSTEM)
    data = _json_object(raw)
    entities = [
        {"name": str(e["name"]).strip(), "type": str(e.get("type", "Other")).strip()}
        for e in data.get("entities", [])
        if isinstance(e, dict) and e.get("name")
    ]
    relationships = [
        {
            "source": str(r["source"]).strip(),
            "relation": str(r.get("relation", "RELATED_TO")).strip(),
            "target": str(r["target"]).strip(),
        }
        for r in data.get("relationships", [])
        if isinstance(r, dict) and r.get("source") and r.get("target")
    ]
    return {"entities": entities, "relationships": relationships}


async def extract_query_entities(query: str) -> list[str]:
    """Return key entity names mentioned in a query (async)."""
    raw = (await llm.generate(query, QUERY_ENTITIES_SYSTEM))["text"]
    return [str(x).strip() for x in _json_array(raw) if str(x).strip()]
