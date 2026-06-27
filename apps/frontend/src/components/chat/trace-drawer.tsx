"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Cpu } from "lucide-react";
import type { AgentTraceStep } from "@/lib/types";

const LABELS: Record<string, string> = {
  planner: "Planned strategy",
  executor: "Retrieved context",
  evaluator: "Evaluated sufficiency",
  retry: "Retried",
  web_search: "Searched the web",
  answer: "Generated answer",
};

function detail(step: AgentTraceStep): string {
  const parts: string[] = [];
  if (step.tool) parts.push(`tool: ${step.tool}`);
  if (step.reasoning) parts.push(String(step.reasoning));
  if (step.chunks != null) parts.push(`${step.chunks} chunks · ${step.relationships} relationships`);
  if (step.sufficient != null) parts.push(step.sufficient ? "sufficient" : "insufficient");
  if (step.reason) parts.push(String(step.reason));
  if (step.results != null) parts.push(`${step.results} web results`);
  if (step.action) parts.push(String(step.action));
  return parts.join(" · ");
}

export function TraceDrawer({ trace }: { trace: AgentTraceStep[] }) {
  const [open, setOpen] = useState(true);
  if (!trace.length) return null;
  return (
    <div className="rounded-[var(--radius-card)] border bg-surface-1">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-2 px-4 py-2 text-sm font-medium"
      >
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        <Cpu className="h-4 w-4 text-primary" />
        Agent reasoning · {trace.length} steps
      </button>
      {open && (
        <ol className="flex flex-col gap-2 border-t px-4 py-3 text-xs">
          {trace.map((s, i) => (
            <li key={i} className="flex gap-2">
              <span className="font-mono text-muted-foreground">{i + 1}.</span>
              <div className="min-w-0">
                <span className="font-medium">{LABELS[s.node] ?? s.node}</span>
                {detail(s) && <p className="text-muted-foreground">{detail(s)}</p>}
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
