"use client";

import { MessageSquare, Plus, Trash2 } from "lucide-react";
import { useChatSessions, useDeleteChatSession } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ChatSidebar({
  selectedId,
  onSelect,
  onNew,
  onDeleted,
}: {
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDeleted: (id: string) => void;
}) {
  const { data: sessions } = useChatSessions();
  const del = useDeleteChatSession();

  async function handleDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    await del.mutateAsync(id);
    onDeleted(id);
  }

  return (
    <div className="flex h-full w-72 shrink-0 flex-col border-r bg-surface-1">
      <div className="p-3">
        <Button className="w-full" onClick={onNew}>
          <Plus className="h-4 w-4" />
          New chat
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-3">
        {!sessions?.length ? (
          <p className="px-3 py-4 text-xs text-muted-foreground">No conversations yet.</p>
        ) : (
          sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => onSelect(s.id)}
              className={cn(
                "group flex w-full items-center gap-2 rounded-[var(--radius-button)] px-3 py-2 text-left text-sm transition-colors",
                selectedId === s.id ? "bg-surface-3" : "hover:bg-surface-2",
              )}
            >
              <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
              <span className="flex-1 truncate">{s.title}</span>
              <Trash2
                onClick={(e) => handleDelete(e, s.id)}
                className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100"
              />
            </button>
          ))
        )}
      </div>
    </div>
  );
}
