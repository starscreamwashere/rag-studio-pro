import { FileText } from "lucide-react";
import type { ChatCitation } from "@/lib/types";

export function SourceCards({ citations }: { citations: ChatCitation[] }) {
  if (!citations.length) return null;
  return (
    <div className="mt-3 flex flex-col gap-2">
      <p className="text-xs font-medium text-muted-foreground">Sources</p>
      <div className="grid gap-2 sm:grid-cols-2">
        {citations.map((c) => (
          <div
            key={`${c.index}-${c.document_id}`}
            className="rounded-[var(--radius-button)] border bg-surface-1 p-3 text-xs"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="flex min-w-0 items-center gap-1.5 font-medium">
                <span className="font-mono text-primary">[{c.index}]</span>
                <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                <span className="truncate">{c.file_name}</span>
              </span>
              <span className="shrink-0 text-muted-foreground">{Math.round(c.score * 100)}%</span>
            </div>
            <p className="mt-1 line-clamp-3 text-muted-foreground">{c.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
