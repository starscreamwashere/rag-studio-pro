import { Badge, type BadgeVariant } from "@/components/ui/badge";

const MAP: Record<string, { variant: BadgeVariant; label: string }> = {
  // document ingestion statuses
  pending: { variant: "neutral", label: "Pending" },
  processing: { variant: "info", label: "Processing" },
  completed: { variant: "success", label: "Ready" },
  failed: { variant: "error", label: "Failed" },
  // knowledge base statuses
  active: { variant: "success", label: "Active" },
  syncing: { variant: "info", label: "Syncing" },
  archived: { variant: "neutral", label: "Archived" },
};

export function StatusBadge({ status }: { status: string }) {
  const s = MAP[status] ?? { variant: "neutral" as BadgeVariant, label: status };
  return <Badge variant={s.variant}>{s.label}</Badge>;
}
