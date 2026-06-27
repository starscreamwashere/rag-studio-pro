"use client";

import { ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { useAuditLogs, useMe, useUsage } from "@/lib/hooks";

const MANAGE_USERS = "users:manage";

export default function AdminPage() {
  const { data: user } = useMe();
  const isAdmin = !!user?.role.permissions.includes(MANAGE_USERS);
  const { data: usage } = useUsage(isAdmin);
  const { data: logs } = useAuditLogs(isAdmin);

  if (user && !isAdmin) {
    return (
      <>
        <PageHeader title="Admin" description="User management, quotas, and audit monitoring." />
        <div className="flex flex-col items-center justify-center gap-2 px-8 py-24 text-center">
          <ShieldCheck className="h-8 w-8 text-muted-foreground" />
          <p className="font-medium">Admin access required</p>
          <p className="text-sm text-muted-foreground">
            Your role ({user.role.name}) can’t view the admin module.
          </p>
        </div>
      </>
    );
  }

  const stats = [
    { label: "Knowledge bases", value: usage?.knowledge_bases ?? 0 },
    { label: "Documents", value: usage?.documents ?? 0 },
    { label: "Experiments", value: usage?.experiments ?? 0 },
    { label: "Audit events", value: usage?.audit_events ?? 0 },
  ];

  return (
    <>
      <PageHeader title="Admin" description="Usage and audit monitoring." />
      <div className="flex flex-col gap-8 px-8 py-6">
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="rounded-[var(--radius-card)] border bg-card p-5">
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight tabular-nums">{s.value}</p>
            </div>
          ))}
        </section>

        <section className="flex flex-col gap-2">
          <h2 className="text-sm font-medium text-muted-foreground">Audit log</h2>
          {!logs?.length ? (
            <p className="text-sm text-muted-foreground">No audit events yet.</p>
          ) : (
            <div className="overflow-hidden rounded-[var(--radius-card)] border">
              <table className="w-full text-sm">
                <thead className="bg-surface-2 text-xs text-muted-foreground">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Time</th>
                    <th className="px-4 py-2 text-left font-medium">Action</th>
                    <th className="px-4 py-2 text-left font-medium">Resource</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((l) => (
                    <tr key={l.id} className="border-t">
                      <td className="px-4 py-2 text-muted-foreground">
                        {new Date(l.timestamp).toLocaleString()}
                      </td>
                      <td className="px-4 py-2 font-mono text-xs">{l.action}</td>
                      <td className="px-4 py-2 text-muted-foreground">{l.resource_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </>
  );
}
