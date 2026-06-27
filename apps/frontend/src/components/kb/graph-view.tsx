"use client";

import { Badge } from "@/components/ui/badge";
import { useGraphEntities, useGraphRelationships } from "@/lib/hooks";

function GraphEmpty() {
  return (
    <div className="rounded-[var(--radius-card)] border border-dashed px-6 py-12 text-center text-sm text-muted-foreground">
      No graph yet. Entities and relationships are extracted automatically when you upload
      documents.
    </div>
  );
}

export function EntitiesView({ kbId }: { kbId: string }) {
  const { data, isLoading } = useGraphEntities(kbId, true);
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!data?.length) return <GraphEmpty />;
  return (
    <div className="flex flex-col gap-2">
      {data.map((e) => (
        <div
          key={e.id ?? e.name}
          className="flex items-center justify-between rounded-[var(--radius-button)] border bg-card px-4 py-2.5"
        >
          <span className="flex items-center gap-2 text-sm">
            <span className="font-medium">{e.name}</span>
            {e.type && <Badge variant="info">{e.type}</Badge>}
          </span>
          <span className="text-xs text-muted-foreground">
            {e.degree} connection{e.degree === 1 ? "" : "s"}
          </span>
        </div>
      ))}
    </div>
  );
}

export function RelationsView({ kbId }: { kbId: string }) {
  const { data, isLoading } = useGraphRelationships(kbId, true);
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!data?.length) return <GraphEmpty />;
  return (
    <div className="flex flex-col gap-2">
      {data.map((r, i) => (
        <div
          key={`${r.source}-${r.relation}-${r.target}-${i}`}
          className="flex flex-wrap items-center gap-2 rounded-[var(--radius-button)] border bg-card px-4 py-2.5 text-sm"
        >
          <span className="font-medium">{r.source}</span>
          <span className="rounded bg-surface-2 px-2 py-0.5 font-mono text-xs text-muted-foreground">
            {r.relation.replace(/_/g, " ").toLowerCase()}
          </span>
          <span className="font-medium">{r.target}</span>
        </div>
      ))}
    </div>
  );
}
