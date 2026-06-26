"use client";

import { useEffect, useState } from "react";

type Status = "checking" | "ok" | "down";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const STYLES: Record<Status, { dot: string; label: string }> = {
  checking: { dot: "bg-warning", label: "Checking API…" },
  ok: { dot: "bg-success", label: "API healthy" },
  down: { dot: "bg-destructive", label: "API unreachable" },
};

/** Pings the backend `/health` endpoint to confirm the stack is wired up. */
export function HealthBadge() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let active = true;
    fetch(`${API_URL}/health`)
      .then((res) => (active ? setStatus(res.ok ? "ok" : "down") : null))
      .catch(() => (active ? setStatus("down") : null));
    return () => {
      active = false;
    };
  }, []);

  const { dot, label } = STYLES[status];

  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-surface-2 px-3 py-1 text-xs font-medium">
      <span className={`h-2 w-2 rounded-full ${dot}`} />
      {label}
    </span>
  );
}
