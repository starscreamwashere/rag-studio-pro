"use client";

import { PageHeader } from "@/components/app/page-header";
import { useCurrentOrganization, useKnowledgeBases, useMe, useWorkspaces } from "@/lib/hooks";

export default function DashboardPage() {
  const { data: user } = useMe();
  const { data: org } = useCurrentOrganization();
  const { data: workspaces } = useWorkspaces();
  const { data: kbs } = useKnowledgeBases();

  const documentTotal = kbs?.reduce((sum, kb) => sum + kb.document_count, 0) ?? 0;
  const stats = [
    { label: "Documents indexed", value: String(documentTotal) },
    { label: "Knowledge bases", value: String(kbs?.length ?? 0) },
    { label: "Queries today", value: "0" },
    { label: "Avg. latency", value: "—" },
  ];

  return (
    <>
      <PageHeader
        title={`Welcome${user?.full_name ? `, ${user.full_name}` : ""}`}
        description={org ? `${org.name} · ${org.plan} plan` : "System overview and quick insights"}
      />

      <div className="flex flex-col gap-8 px-8 py-6">
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="rounded-[var(--radius-card)] border bg-card p-5">
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight">{s.value}</p>
            </div>
          ))}
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="text-sm font-medium text-muted-foreground">Workspaces</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {workspaces?.map((w) => (
              <div key={w.id} className="rounded-[var(--radius-card)] border bg-card p-5">
                <p className="font-medium">{w.name}</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {w.description ?? "No description"}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
