"use client";

import { useState } from "react";
import Link from "next/link";
import { ApiError } from "@/lib/api";
import { useCreateChatSession, useKnowledgeBases } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";

export function NewChatDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: (sessionId: string) => void;
}) {
  const { data: kbs } = useKnowledgeBases();
  const create = useCreateChatSession();
  const [kbId, setKbId] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!kbId) return;
    setError(null);
    try {
      const session = await create.mutateAsync({ knowledge_base_id: kbId });
      onCreated(session.id);
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to start chat");
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title="New chat">
      {!kbs?.length ? (
        <div className="flex flex-col gap-3 text-sm">
          <p className="text-muted-foreground">
            You need a knowledge base with documents before you can chat.
          </p>
          <Link href="/knowledge-bases">
            <Button>Go to Knowledge Bases</Button>
          </Link>
        </div>
      ) : (
        <form onSubmit={submit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="kb" className="text-sm font-medium">
              Knowledge base
            </label>
            <select
              id="kb"
              value={kbId}
              onChange={(e) => setKbId(e.target.value)}
              className="h-10 rounded-[var(--radius-button)] border bg-surface-1 px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="" disabled>
                Select a knowledge base
              </option>
              {kbs.map((kb) => (
                <option key={kb.id} value={kb.id}>
                  {kb.name} ({kb.document_count} docs)
                </option>
              ))}
            </select>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={!kbId || create.isPending}>
              {create.isPending ? "Starting…" : "Start chat"}
            </Button>
          </div>
        </form>
      )}
    </Dialog>
  );
}
