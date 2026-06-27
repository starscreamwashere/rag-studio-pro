"use client";

import { useKnowledgeBases } from "@/lib/hooks";
import type { RetrievalMode } from "@/lib/types";
import { cn } from "@/lib/utils";

const MODES: RetrievalMode[] = ["vector", "graph", "hybrid"];

interface Props {
  kbId: string;
  setKbId: (v: string) => void;
  mode: RetrievalMode;
  setMode: (v: RetrievalMode) => void;
  topK: number;
  setTopK: (v: number) => void;
  fusion: "rrf" | "weighted";
  setFusion: (v: "rrf" | "weighted") => void;
  alpha: number;
  setAlpha: (v: number) => void;
}

export function ControlPanel(p: Props) {
  const { data: kbs } = useKnowledgeBases();

  return (
    <aside className="flex w-80 shrink-0 flex-col gap-5 overflow-y-auto border-r p-5">
      <h2 className="text-sm font-semibold">Retrieval controls</h2>

      <Field label="Knowledge base">
        <select
          value={p.kbId}
          onChange={(e) => p.setKbId(e.target.value)}
          className="h-9 w-full rounded-[var(--radius-button)] border bg-surface-1 px-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="" disabled>
            Select a knowledge base
          </option>
          {kbs?.map((kb) => (
            <option key={kb.id} value={kb.id}>
              {kb.name}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Retrieval mode">
        <div className="flex gap-1 rounded-[var(--radius-button)] bg-surface-2 p-1">
          {MODES.map((m) => (
            <button
              key={m}
              onClick={() => p.setMode(m)}
              className={cn(
                "flex-1 rounded-[8px] px-2 py-1.5 text-xs font-medium capitalize transition-colors",
                p.mode === m ? "bg-card text-primary shadow-sm" : "text-muted-foreground",
              )}
            >
              {m}
            </button>
          ))}
        </div>
      </Field>

      {p.mode !== "graph" && (
        <Field label={`Top-K · ${p.topK}`}>
          <input
            type="range"
            min={1}
            max={20}
            value={p.topK}
            onChange={(e) => p.setTopK(Number(e.target.value))}
            className="w-full accent-[var(--primary)]"
          />
        </Field>
      )}

      {p.mode === "hybrid" && (
        <>
          <Field label="Score fusion">
            <div className="flex gap-1 rounded-[var(--radius-button)] bg-surface-2 p-1">
              {(["rrf", "weighted"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => p.setFusion(f)}
                  className={cn(
                    "flex-1 rounded-[8px] px-2 py-1.5 text-xs font-medium uppercase transition-colors",
                    p.fusion === f ? "bg-card text-primary shadow-sm" : "text-muted-foreground",
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
          </Field>
          {p.fusion === "weighted" && (
            <Field label={`Vector ↔ Lexical weight · ${p.alpha.toFixed(2)}`}>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={p.alpha}
                onChange={(e) => p.setAlpha(Number(e.target.value))}
                className="w-full accent-[var(--primary)]"
              />
            </Field>
          )}
        </>
      )}

      <p className="mt-auto text-xs text-muted-foreground">
        Chunking &amp; embedding model are set per knowledge base at creation.
      </p>
    </aside>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
