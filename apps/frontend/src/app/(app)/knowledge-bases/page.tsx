"use client";

import { useState } from "react";
import Link from "next/link";
import { Database, Plus, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { CreateKnowledgeBaseDialog } from "@/components/kb/create-kb-dialog";
import { StatusBadge } from "@/components/kb/status-badge";
import { Button } from "@/components/ui/button";
import { useDeleteKnowledgeBase, useKnowledgeBases } from "@/lib/hooks";

export default function KnowledgeBasesPage() {
  const { data: kbs, isLoading } = useKnowledgeBases();
  const del = useDeleteKnowledgeBase();
  const [createOpen, setCreateOpen] = useState(false);

  async function handleDelete(e: React.MouseEvent, id: string, name: string) {
    e.preventDefault();
    if (confirm(`Delete "${name}" and all its documents? This cannot be undone.`)) {
      await del.mutateAsync(id);
    }
  }

  return (
    <>
      <PageHeader title="Knowledge Bases" description="Manage knowledge collections." />

      <div className="px-8 py-6">
        <div className="mb-6 flex justify-end">
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" />
            New knowledge base
          </Button>
        </div>

        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : !kbs?.length ? (
          <div className="flex flex-col items-center gap-3 rounded-[var(--radius-card)] border border-dashed px-6 py-20 text-center">
            <Database className="h-8 w-8 text-muted-foreground" />
            <p className="font-medium">No knowledge bases yet</p>
            <p className="max-w-sm text-sm text-muted-foreground">
              Create your first knowledge base, then upload documents to make them searchable.
            </p>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4" />
              Create your first knowledge base
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {kbs.map((kb) => (
              <Link
                key={kb.id}
                href={`/knowledge-bases/${kb.id}`}
                className="group flex flex-col gap-3 rounded-[var(--radius-card)] border bg-card p-5 transition-colors hover:border-primary/40"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-medium">{kb.name}</span>
                  <StatusBadge status={kb.status} />
                </div>
                <p className="line-clamp-2 min-h-[2.5rem] text-sm text-muted-foreground">
                  {kb.description ?? "No description"}
                </p>
                <div className="flex items-center justify-between border-t pt-3">
                  <span className="text-xs text-muted-foreground">
                    {kb.document_count} document{kb.document_count === 1 ? "" : "s"}
                  </span>
                  <button
                    onClick={(e) => handleDelete(e, kb.id, kb.name)}
                    aria-label="Delete knowledge base"
                    className="text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <CreateKnowledgeBaseDialog open={createOpen} onClose={() => setCreateOpen(false)} />
    </>
  );
}
