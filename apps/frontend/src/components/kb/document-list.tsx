"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { StatusBadge } from "@/components/kb/status-badge";
import { useDocumentJob } from "@/lib/hooks";
import type { Document } from "@/lib/types";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function DocumentRow({ doc }: { doc: Document }) {
  const qc = useQueryClient();
  const active = doc.ingestion_status === "pending" || doc.ingestion_status === "processing";
  const { data: job } = useDocumentJob(doc.id, active);

  // When the job finishes, refresh the document list and KB doc counts.
  useEffect(() => {
    if (job?.status === "completed" || job?.status === "failed") {
      qc.invalidateQueries({ queryKey: ["knowledge-bases", doc.knowledge_base_id, "documents"] });
      qc.invalidateQueries({ queryKey: ["knowledge-bases"] });
    }
  }, [job?.status, doc.knowledge_base_id, qc]);

  const status = job?.status ?? doc.ingestion_status;
  const showProgress = status === "processing" || status === "pending" || status === "queued";

  return (
    <div className="flex items-center gap-4 border-b px-4 py-3 last:border-b-0">
      <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{doc.file_name}</p>
        <p className="text-xs text-muted-foreground">
          {doc.file_type.toUpperCase()} · {formatSize(doc.file_size)}
        </p>
        {showProgress && (
          <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-surface-3">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${job?.progress_percent ?? 5}%` }}
            />
          </div>
        )}
        {job?.status === "failed" && job.error_message && (
          <p className="mt-1 text-xs text-destructive">{job.error_message}</p>
        )}
      </div>
      <StatusBadge status={status === "queued" ? "pending" : status} />
    </div>
  );
}

export function DocumentList({ documents }: { documents: Document[] }) {
  if (documents.length === 0) {
    return (
      <div className="rounded-[var(--radius-card)] border border-dashed px-6 py-12 text-center text-sm text-muted-foreground">
        No documents yet. Upload one to start building this knowledge base.
      </div>
    );
  }
  return (
    <div className="rounded-[var(--radius-card)] border bg-card">
      {documents.map((doc) => (
        <DocumentRow key={doc.id} doc={doc} />
      ))}
    </div>
  );
}
