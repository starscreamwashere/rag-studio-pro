"use client";

import { use, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { DocumentList } from "@/components/kb/document-list";
import { DocumentUpload } from "@/components/kb/document-upload";
import { StatusBadge } from "@/components/kb/status-badge";
import { useDocuments, useKnowledgeBase } from "@/lib/hooks";
import { cn } from "@/lib/utils";

const TABS = [
  { key: "documents", label: "Documents", phase: 2 },
  { key: "entities", label: "Entities", phase: 5 },
  { key: "relations", label: "Relations", phase: 5 },
  { key: "settings", label: "Settings", phase: 8 },
] as const;

export default function KnowledgeBaseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: kb } = useKnowledgeBase(id);
  const { data: documents } = useDocuments(id);
  const [tab, setTab] = useState<(typeof TABS)[number]["key"]>("documents");

  const active = TABS.find((t) => t.key === tab)!;

  return (
    <>
      <div className="border-b px-8 py-6">
        <Link
          href="/knowledge-bases"
          className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Knowledge Bases
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">{kb?.name ?? "…"}</h1>
          {kb && <StatusBadge status={kb.status} />}
        </div>
        {kb?.description && (
          <p className="mt-1 text-sm text-muted-foreground">{kb.description}</p>
        )}

        <div className="mt-5 flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "rounded-[var(--radius-button)] px-3 py-1.5 text-sm transition-colors",
                t.key === tab
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-surface-2",
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-8 py-6">
        {tab === "documents" ? (
          <div className="flex flex-col gap-6">
            <DocumentUpload kbId={id} />
            <DocumentList documents={documents ?? []} />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 py-20 text-center">
            <span className="rounded-full bg-surface-2 px-3 py-1 font-mono text-xs text-muted-foreground">
              Ships in Phase {active.phase}
            </span>
            <p className="text-sm text-muted-foreground">
              The {active.label} view is part of a later phase.
            </p>
          </div>
        )}
      </div>
    </>
  );
}
