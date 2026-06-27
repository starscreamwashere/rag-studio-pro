"""LangGraph agentic workflow.

Nodes: planner -> executor(retrieve) -> evaluator -> {retry/escalate | web_search | answer}.
The planner selects an internal retrieval tool (vector/graph/hybrid) and whether
external web search would help; the evaluator decides sufficiency; web search is
gated by human approval. Memory comes from the chat session's recent history.
"""

import json
import operator
from typing import Annotated, TypedDict

from starlette.concurrency import run_in_threadpool

from app.agent import tools
from app.integrations import llm
from app.integrations.llm import LLMError, LLMNotConfigured
from app.models.knowledge_base import KnowledgeBase
from app.rag import graph_retrieval, hybrid, retrieval

PLAN_SYSTEM = (
    "You are the planning step of a retrieval agent. Choose how to answer the question. "
    'Return ONLY JSON: {"internal_tool": "vector|graph|hybrid", "needs_web": bool, '
    '"wants_report": bool, "reasoning": str}. '
    "Use 'graph' for relationship/dependency/ownership/org-structure questions, 'hybrid' for "
    "mixed questions, 'vector' for plain factual lookups. Set needs_web true only when the "
    "answer likely needs current public information not in internal documents."
)
EVAL_SYSTEM = (
    "You judge whether the retrieved context is sufficient to answer the question. "
    'Return ONLY JSON: {"sufficient": bool, "reason": str}.'
)
ANSWER_SYSTEM = (
    "You are an enterprise knowledge assistant. Answer using ONLY the provided context "
    "(internal documents, knowledge-graph relationships, and any web results). Cite internal "
    "sources inline as [n]. If the context is insufficient, say so."
)
REPORT_SYSTEM = (
    "You are an enterprise analyst. Produce a structured markdown report (with headings and "
    "bullet points) answering the request using ONLY the provided context. Cite sources as [n]."
)


class AgentState(TypedDict, total=False):
    query: str
    history: list
    allow_web_search: bool
    tool: str
    needs_web: bool
    wants_report: bool
    attempts: int
    sufficient: bool
    chunks: list
    triples: list
    web_results: list
    web_done: bool
    answer: str
    generation_error: str | None
    needs_approval: bool
    trace: Annotated[list, operator.add]


def _json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}


async def _safe_generate(prompt: str, system: str) -> tuple[str, str | None]:
    try:
        return (await llm.generate(prompt, system))["text"], None
    except LLMNotConfigured:
        return "", "No LLM provider is configured."
    except LLMError as exc:
        return "", str(exc)


def _history_block(history: list) -> str:
    if not history:
        return ""
    turns = "\n".join(f"{r}: {c}" for r, c in history[-6:])
    return f"Conversation so far:\n{turns}\n\n"


def build_agent_graph(kb: KnowledgeBase):
    from langgraph.graph import END, START, StateGraph

    async def plan(state: AgentState) -> dict:
        prompt = (
            f"{_history_block(state.get('history', []))}Question: {state['query']}\n\n"
            "Plan the retrieval."
        )
        raw, _ = await _safe_generate(prompt, PLAN_SYSTEM)
        data = _json(raw)
        tool = data.get("internal_tool")
        if tool not in ("vector", "graph", "hybrid"):
            tool = "hybrid"
        return {
            "tool": tool,
            "needs_web": bool(data.get("needs_web")),
            "wants_report": bool(data.get("wants_report")),
            "attempts": 0,
            "web_done": False,
            "trace": [
                {
                    "node": "planner",
                    "tool": tool,
                    "needs_web": bool(data.get("needs_web")),
                    "reasoning": data.get("reasoning", ""),
                }
            ],
        }

    async def retrieve_node(state: AgentState) -> dict:
        tool = state["tool"]
        chunks: list = []
        triples: list = []
        if tool == "vector":
            chunks = await retrieval.retrieve(kb, state["query"])
        elif tool == "hybrid":
            chunks = await hybrid.hybrid_retrieve(kb, state["query"])
        if tool in ("graph", "hybrid"):
            triples, _ = await graph_retrieval.retrieve(kb.id, state["query"])
        return {
            "chunks": chunks,
            "triples": triples,
            "trace": [
                {
                    "node": "executor",
                    "tool": tool,
                    "chunks": len(chunks),
                    "relationships": len(triples),
                }
            ],
        }

    async def evaluate(state: AgentState) -> dict:
        ctx = "\n".join(c.text[:300] for c in state.get("chunks", [])[:4])
        rels = "\n".join(
            f"{t['source']} {t['relation']} {t['target']}" for t in state.get("triples", [])[:8]
        )
        prompt = f"Question: {state['query']}\n\nContext:\n{ctx}\n{rels}\n\nIs this sufficient?"
        raw, _ = await _safe_generate(prompt, EVAL_SYSTEM)
        data = _json(raw)
        sufficient = bool(data.get("sufficient", bool(state.get("chunks") or state.get("triples"))))
        return {
            "sufficient": sufficient,
            "trace": [
                {"node": "evaluator", "sufficient": sufficient, "reason": data.get("reason", "")}
            ],
        }

    async def escalate(state: AgentState) -> dict:
        return {
            "tool": "hybrid",
            "attempts": state.get("attempts", 0) + 1,
            "trace": [{"node": "retry", "action": "escalate to hybrid retrieval"}],
        }

    async def web_search_node(state: AgentState) -> dict:
        results = await run_in_threadpool(tools.web_search, state["query"])
        return {
            "web_results": results,
            "web_done": True,
            "trace": [{"node": "web_search", "results": len(results)}],
        }

    async def answer(state: AgentState) -> dict:
        chunks = state.get("chunks", [])
        triples = state.get("triples", [])
        web = state.get("web_results", [])
        context = "\n\n".join(f"[{i + 1}] {c.text}" for i, c in enumerate(chunks))
        if triples:
            facts = "\n".join(
                f"- {t['source']} {t['relation'].replace('_', ' ').lower()} {t['target']}"
                for t in triples
            )
            context += f"\n\nKnowledge graph:\n{facts}"
        if web:
            web_block = "\n".join(f"- {w['title']}: {w['snippet']} ({w['url']})" for w in web)
            context += f"\n\nWeb results:\n{web_block}"
        prompt = (
            f"{_history_block(state.get('history', []))}Context:\n{context}\n\n"
            f"Question: {state['query']}\n\nAnswer:"
        )
        system = REPORT_SYSTEM if state.get("wants_report") else ANSWER_SYSTEM
        text, error = await _safe_generate(prompt, system)
        needs_approval = (
            bool(state.get("needs_web"))
            and not state.get("allow_web_search")
            and not state.get("web_done")
        )
        return {
            "answer": text,
            "generation_error": error,
            "needs_approval": needs_approval,
            "trace": [{"node": "answer", "report": bool(state.get("wants_report"))}],
        }

    def route_after_eval(state: AgentState) -> str:
        if state.get("sufficient"):
            return "answer"
        if state.get("needs_web") and state.get("allow_web_search") and not state.get("web_done"):
            return "web_search"
        if state.get("attempts", 0) < 1 and state.get("tool") != "hybrid":
            return "escalate"
        return "answer"

    g = StateGraph(AgentState)
    g.add_node("plan", plan)
    g.add_node("retrieve", retrieve_node)
    g.add_node("evaluate", evaluate)
    g.add_node("escalate", escalate)
    g.add_node("web_search", web_search_node)
    g.add_node("answer", answer)
    g.add_edge(START, "plan")
    g.add_edge("plan", "retrieve")
    g.add_edge("retrieve", "evaluate")
    g.add_conditional_edges(
        "evaluate",
        route_after_eval,
        {"answer": "answer", "web_search": "web_search", "escalate": "escalate"},
    )
    g.add_edge("escalate", "retrieve")
    g.add_edge("web_search", "answer")
    g.add_edge("answer", END)
    return g.compile()


async def run_agent(
    kb: KnowledgeBase, query: str, history: list, allow_web_search: bool
) -> AgentState:
    graph = build_agent_graph(kb)
    return await graph.ainvoke(
        {
            "query": query,
            "history": history,
            "allow_web_search": allow_web_search,
            "attempts": 0,
            "trace": [],
        }
    )
