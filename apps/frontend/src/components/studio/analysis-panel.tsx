"use client";

import type { ExperimentResponse } from "@/lib/types";

export function AnalysisPanel({ result }: { result: ExperimentResponse | null }) {
  return (
    <aside className="flex w-96 shrink-0 flex-col gap-5 overflow-y-auto border-l p-5">
      <h2 className="text-sm font-semibold">Analysis</h2>

      {!result ? (
        <p className="text-sm text-muted-foreground">Run an experiment to see retrieval analysis.</p>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-2">
            <Metric label="Latency" value={`${result.metrics.latency_ms} ms`} />
            <Metric
              label="Retrieval score"
              value={result.metrics.score != null ? result.metrics.score.toFixed(3) : "—"}
            />
            <Metric label="Tokens" value={result.metrics.token_usage ?? "—"} />
            <Metric label="Chunks" value={result.metrics.retrieved_count} />
            <Metric label="Relationships" value={result.metrics.relationship_count} />
          </div>

          {result.vector_results.length > 0 && (
            <section className="flex flex-col gap-2">
              <h3 className="text-xs font-medium text-muted-foreground">Retrieved chunks</h3>
              {result.vector_results.map((c) => (
                <div key={c.chunk_id} className="rounded-[var(--radius-button)] border bg-card p-3 text-xs">
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="truncate font-medium">{c.file_name}</span>
                    <span className="shrink-0 font-mono text-muted-foreground">
                      {c.fused_score != null
                        ? `fused ${c.fused_score.toFixed(3)}`
                        : `score ${c.score.toFixed(3)}`}
                    </span>
                  </div>
                  {(c.vector_score != null || c.lexical_score != null) && (
                    <div className="mb-1 flex gap-3 font-mono text-[10px] text-muted-foreground">
                      {c.vector_score != null && <span>vec {c.vector_score.toFixed(3)}</span>}
                      {c.lexical_score != null && <span>lex {c.lexical_score.toFixed(3)}</span>}
                    </div>
                  )}
                  <p className="line-clamp-3 text-muted-foreground">{c.text}</p>
                </div>
              ))}
            </section>
          )}

          {result.graph_results.length > 0 && (
            <section className="flex flex-col gap-2">
              <h3 className="text-xs font-medium text-muted-foreground">Graph relationships</h3>
              {result.graph_results.map((t, i) => (
                <div
                  key={`${t.source}-${t.relation}-${t.target}-${i}`}
                  className="flex flex-wrap items-center gap-1.5 rounded-[var(--radius-button)] border bg-card px-3 py-2 text-xs"
                >
                  <span className="font-medium">{t.source}</span>
                  <span className="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
                    {t.relation.replace(/_/g, " ").toLowerCase()}
                  </span>
                  <span className="font-medium">{t.target}</span>
                </div>
              ))}
            </section>
          )}
        </>
      )}
    </aside>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-[var(--radius-button)] border bg-card p-3">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}
