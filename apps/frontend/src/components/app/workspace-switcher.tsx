"use client";

import { ChevronsUpDown } from "lucide-react";
import { useWorkspaces } from "@/lib/hooks";

/** Phase 1: displays the current workspace. Switching lands in a later phase. */
export function WorkspaceSwitcher() {
  const { data: workspaces, isLoading } = useWorkspaces();
  const current = workspaces?.[0];

  return (
    <button
      type="button"
      className="flex w-full items-center justify-between rounded-[var(--radius-button)] border bg-card px-3 py-2 text-sm"
    >
      <span className="truncate">
        {isLoading ? "Loading…" : (current?.name ?? "No workspace")}
      </span>
      <ChevronsUpDown className="h-4 w-4 text-muted-foreground" />
    </button>
  );
}
