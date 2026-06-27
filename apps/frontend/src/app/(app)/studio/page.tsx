"use client";

import { useState } from "react";
import Link from "next/link";
import { FlaskConical, Play } from "lucide-react";
import { AnalysisPanel } from "@/components/studio/analysis-panel";
import { ControlPanel } from "@/components/studio/control-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useExperimentRuns, useKnowledgeBases, useRunExperiment, useWorkspaces } from "@/lib/hooks";
import type { ExperimentResponse, RetrievalMode } from "@/lib/types";

export default function StudioPage() {
  const { data: kbs } = useKnowledgeBases();
  const { data: workspaces } = useWorkspaces();
  const workspaceId = workspaces?.[0]?.id ?? null;
  const { data: runs } = useExperimentRuns(workspaceId);
  const runExperiment = useRunExperiment();

  const [kbId, setKbId] = useState("");
  const [mode, setMode] = useState<RetrievalMode>("hybrid");
  const [topK, setTopK] = useState(5);
  const [fusion, setFusion] = useState<"rrf" | "weighted">("rrf");
  const [alpha, setAlpha] = useState(0.5);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<ExperimentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    if (!kbId || !query.trim()) return;
    setError(null);
    try {
      const res = await runExperiment.mutateAsync({
        knowledge_base_id: kbId,
        query: query.trim(),
        retrieval_mode: mode,
        top_k: topK,
        fusion_strategy: fusion,
        alpha,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Experiment failed");
    }
  }

  if (kbs && kbs.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
        <FlaskConical className="h-10 w-10 text-muted-foreground" />
        <p className="text-lg font-medium">The Studio needs a knowledge base</p>
        <Link href="/knowledge-bases">
          <Button>Create a knowledge base</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      <ControlPanel
        kbId={kbId}
        setKbId={setKbId}
        mode={mode}
        setMode={setMode}
        topK={topK}
        setTopK={setTopK}
        fusion={fusion}
        setFusion={setFusion}
        alpha={alpha}
        setAlpha={setAlpha}
      />

      {/* Center — query console */}
      <div className="flex min-w-0 flex-1 flex-col overflow-y-auto p-6">
        <h1 className="text-xl font-semibold tracking-tight">Studio</h1>
        <p className="mb-4 text-sm text-muted-foreground">
          Experiment with retrieval strategies and compare results in real time.
        </p>

        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "Explain the customer refund workflow"'
          className="min-h-24"
        />
        <div className="mt-3 flex items-center gap-3">
          <Button onClick={run} disabled={!kbId || !query.trim() || runExperiment.isPending}>
            <Play className="h-4 w-4" />
            {runExperiment.isPending ? "Running…" : "Run experiment"}
          </Button>
          {!kbId && <span className="text-xs text-muted-foreground">Select a knowledge base →</span>}
          {error && <span className="text-sm text-destructive">{error}</span>}
        </div>

        {result && (
          <div className="mt-6 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Answer</span>
              <Badge variant="info" className="capitalize">
                {result.retrieval_mode}
              </Badge>
              <span className="font-mono text-xs text-muted-foreground">{result.model}</span>
            </div>
            <div className="rounded-[var(--radius-card)] border bg-card p-4 text-sm whitespace-pre-wrap">
              {result.answer || "—"}
            </div>
            {result.generation_error && (
              <p className="text-xs text-destructive">{result.generation_error}</p>
            )}
          </div>
        )}

        {/* Recent runs comparison */}
        <div className="mt-8">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Recent runs</h2>
          {!runs?.length ? (
            <p className="text-sm text-muted-foreground">No runs yet.</p>
          ) : (
            <div className="overflow-hidden rounded-[var(--radius-card)] border">
              <table className="w-full text-sm">
                <thead className="bg-surface-2 text-xs text-muted-foreground">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium">Time</th>
                    <th className="px-3 py-2 text-left font-medium">Mode</th>
                    <th className="px-3 py-2 text-right font-medium">Top-K</th>
                    <th className="px-3 py-2 text-right font-medium">Latency</th>
                    <th className="px-3 py-2 text-right font-medium">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.slice(0, 12).map((r) => (
                    <tr key={r.id} className="border-t">
                      <td className="px-3 py-2 text-muted-foreground">
                        {new Date(r.created_at).toLocaleTimeString()}
                      </td>
                      <td className="px-3 py-2 capitalize">{r.retrieval_mode}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{r.top_k}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{r.latency_ms} ms</td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {r.score != null ? r.score.toFixed(3) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <AnalysisPanel result={result} />
    </div>
  );
}
