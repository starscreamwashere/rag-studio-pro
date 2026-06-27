"""Neo4j knowledge-graph store (sync driver).

One graph per platform, partitioned by ``kb_id`` on every node. Async callers
wrap these in a threadpool; the Celery worker calls them directly.
"""

import re
import uuid

from neo4j import GraphDatabase

from app.core.config import settings

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _driver


def ensure_schema() -> None:
    with get_driver().session() as s:
        s.run("CREATE INDEX entity_kb IF NOT EXISTS FOR (e:Entity) ON (e.kb_id)")


def _rel_type(relation: str) -> str:
    cleaned = re.sub(r"[^A-Z_]", "_", relation.upper().replace(" ", "_")).strip("_")
    return cleaned[:40] or "RELATED_TO"


def upsert_graph(
    kb_id: str, workspace_id: str, entities: list[dict], relationships: list[dict]
) -> dict[str, str]:
    """MERGE entities + relationships for a KB. Returns {entity_name: node_id}."""
    name_type: dict[str, str] = {}
    for e in entities:
        name_type.setdefault(e["name"], e.get("type", "Other"))
    for r in relationships:
        name_type.setdefault(r["source"], "Other")
        name_type.setdefault(r["target"], "Other")
    if not name_type:
        return {}

    nodes = [{"name": n, "type": t, "id": str(uuid.uuid4())} for n, t in name_type.items()]

    driver = get_driver()
    with driver.session() as s:
        rows = s.run(
            """
            UNWIND $nodes AS n
            MERGE (e:Entity {kb_id: $kb, name: n.name})
            ON CREATE SET e.id = n.id, e.type = n.type, e.workspace_id = $ws
            ON MATCH SET e.type = coalesce(e.type, n.type)
            RETURN n.name AS name, e.id AS id
            """,
            nodes=nodes,
            kb=kb_id,
            ws=workspace_id,
        ).data()
        name_to_id = {row["name"]: row["id"] for row in rows}

        # Group by sanitized relationship type (type can't be parameterized).
        by_type: dict[str, list[dict]] = {}
        for r in relationships:
            by_type.setdefault(_rel_type(r["relation"]), []).append(
                {"source": r["source"], "target": r["target"]}
            )
        for rel_type, rels in by_type.items():
            s.run(
                f"""
                UNWIND $rels AS r
                MATCH (a:Entity {{kb_id: $kb, name: r.source}})
                MATCH (b:Entity {{kb_id: $kb, name: r.target}})
                MERGE (a)-[rr:`{rel_type}`]->(b)
                """,
                rels=rels,
                kb=kb_id,
            )
    return name_to_id


def get_entities(kb_id: str, limit: int = 200) -> list[dict]:
    with get_driver().session() as s:
        return s.run(
            """
            MATCH (e:Entity {kb_id: $kb})
            RETURN e.id AS id, e.name AS name, e.type AS type, count{(e)--()} AS degree
            ORDER BY degree DESC, e.name
            LIMIT $limit
            """,
            kb=kb_id,
            limit=limit,
        ).data()


def get_relationships(kb_id: str, limit: int = 200) -> list[dict]:
    with get_driver().session() as s:
        return s.run(
            """
            MATCH (a:Entity {kb_id: $kb})-[r]->(b:Entity {kb_id: $kb})
            RETURN a.name AS source, type(r) AS relation, b.name AS target
            LIMIT $limit
            """,
            kb=kb_id,
            limit=limit,
        ).data()


def query_subgraph(kb_id: str, terms: list[str], limit: int = 60) -> list[dict]:
    """Relationship triples within N hops of entities matching any search term."""
    if not terms:
        return []
    hops = max(1, min(settings.graph_retrieval_hops, 3))
    with get_driver().session() as s:
        return s.run(
            f"""
            MATCH (seed:Entity {{kb_id: $kb}})
            WHERE any(t IN $terms WHERE toLower(seed.name) CONTAINS t)
            MATCH p = (seed)-[*1..{hops}]-(o:Entity {{kb_id: $kb}})
            UNWIND relationships(p) AS rel
            WITH DISTINCT startNode(rel) AS a, rel, endNode(rel) AS b
            RETURN a.name AS source, type(rel) AS relation, b.name AS target
            LIMIT $limit
            """,
            kb=kb_id,
            terms=[t.lower() for t in terms],
            limit=limit,
        ).data()


def stats(kb_id: str) -> dict:
    with get_driver().session() as s:
        entities = s.run("MATCH (e:Entity {kb_id: $kb}) RETURN count(e) AS c", kb=kb_id).single()[
            "c"
        ]
        rels = s.run(
            "MATCH (:Entity {kb_id: $kb})-[r]->(:Entity {kb_id: $kb}) RETURN count(r) AS c",
            kb=kb_id,
        ).single()["c"]
    return {"entities": entities, "relationships": rels}


def delete_kb_graph(kb_id: str) -> None:
    with get_driver().session() as s:
        s.run("MATCH (e:Entity {kb_id: $kb}) DETACH DELETE e", kb=kb_id)
