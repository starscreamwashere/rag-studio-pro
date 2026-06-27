"use client";

import { useState } from "react";
import Link from "next/link";
import { Check, Database } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { DocumentList } from "@/components/kb/document-list";
import { DocumentUpload } from "@/components/kb/document-upload";
import { Button } from "@/components/ui/button";
import { useDocuments, useKnowledgeBases } from "@/lib/hooks";
import { cn } from "@/lib/utils";

const STEPS = ["Select knowledge base", "Upload", "Parse & process"];

function IngestionTracker({ kbId }: { kbId: string }) {
  const { data: documents } = useDocuments(kbId);
  return (
    <div className="flex flex-col gap-6">
      <DocumentUpload kbId={kbId} />
      <DocumentList documents={documents ?? []} />
    </div>
  );
}

export default function IngestionPage() {
  const { data: kbs, isLoading } = useKnowledgeBases();
  const [kbId, setKbId] = useState<string | null>(null);
  const currentStep = kbId ? 1 : 0;

  return (
    <>
      <PageHeader title="Ingestion" description="Ingest documents and external sources." />

      <div className="px-8 py-6">
        {/* Stepper */}
        <ol className="mb-8 flex items-center gap-4">
          {STEPS.map((label, i) => (
            <li key={label} className="flex items-center gap-2">
              <span
                className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium",
                  i < currentStep
                    ? "bg-primary text-primary-foreground"
                    : i === currentStep
                      ? "bg-primary/10 text-primary"
                      : "bg-surface-2 text-muted-foreground",
                )}
              >
                {i < currentStep ? <Check className="h-4 w-4" /> : i + 1}
              </span>
              <span
                className={cn(
                  "text-sm",
                  i <= currentStep ? "font-medium" : "text-muted-foreground",
                )}
              >
                {label}
              </span>
              {i < STEPS.length - 1 && <span className="ml-2 h-px w-8 bg-border" />}
            </li>
          ))}
        </ol>

        {!kbId ? (
          isLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : !kbs?.length ? (
            <div className="flex flex-col items-center gap-3 rounded-[var(--radius-card)] border border-dashed px-6 py-16 text-center">
              <Database className="h-8 w-8 text-muted-foreground" />
              <p className="font-medium">No knowledge bases yet</p>
              <Link href="/knowledge-bases">
                <Button>Create one first</Button>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <p className="text-sm text-muted-foreground">
                Choose a knowledge base to ingest into:
              </p>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {kbs.map((kb) => (
                  <button
                    key={kb.id}
                    onClick={() => setKbId(kb.id)}
                    className="flex flex-col items-start gap-1 rounded-[var(--radius-card)] border bg-card p-4 text-left transition-colors hover:border-primary/40"
                  >
                    <span className="font-medium">{kb.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {kb.document_count} document{kb.document_count === 1 ? "" : "s"}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )
        ) : (
          <div className="flex flex-col gap-4">
            <button
              onClick={() => setKbId(null)}
              className="self-start text-sm text-muted-foreground hover:text-foreground"
            >
              ← Choose a different knowledge base
            </button>
            <IngestionTracker kbId={kbId} />
          </div>
        )}
      </div>
    </>
  );
}
