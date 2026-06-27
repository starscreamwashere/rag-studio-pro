"use client";

import { useState } from "react";
import { ApiError } from "@/lib/api";
import { useCreateKnowledgeBase, useWorkspaces } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function CreateKnowledgeBaseDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { data: workspaces } = useWorkspaces();
  const create = useCreateKnowledgeBase();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const workspace = workspaces?.[0];

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!workspace) return;
    setError(null);
    try {
      await create.mutateAsync({
        workspace_id: workspace.id,
        name,
        description: description || undefined,
      });
      setName("");
      setDescription("");
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create knowledge base");
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title="Create knowledge base">
      <form onSubmit={submit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="kb-name" className="text-sm font-medium">
            Name
          </label>
          <Input
            id="kb-name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Engineering Docs"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="kb-desc" className="text-sm font-medium">
            Description <span className="text-muted-foreground">(optional)</span>
          </label>
          <Textarea
            id="kb-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What lives in this knowledge base?"
          />
        </div>
        <p className="text-xs text-muted-foreground">
          Created in workspace <span className="font-medium">{workspace?.name ?? "…"}</span>
        </p>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={create.isPending || !workspace}>
            {create.isPending ? "Creating…" : "Create"}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
