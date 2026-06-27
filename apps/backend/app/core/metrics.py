"""Custom Prometheus metrics (scraped from /metrics)."""

from prometheus_client import Counter, Histogram

llm_requests_total = Counter(
    "rag_llm_requests_total", "LLM generation requests", ["provider", "status"]
)
llm_tokens_total = Counter("rag_llm_tokens_total", "LLM tokens consumed", ["provider"])
llm_latency_seconds = Histogram("rag_llm_latency_seconds", "LLM call latency", ["provider"])
ingestion_failures_total = Counter("rag_ingestion_failures_total", "Document ingestion failures")
rate_limit_rejections_total = Counter(
    "rag_rate_limit_rejections_total", "Requests rejected by rate limit / quota", ["reason"]
)
