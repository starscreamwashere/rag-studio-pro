import { HealthBadge } from "@/components/health-badge";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 px-6 py-16">
      <div className="flex flex-col gap-3">
        <span className="font-mono text-sm text-muted-foreground">Phase 0 · Foundation</span>
        <h1 className="text-4xl font-semibold tracking-tight">RAG Studio Pro</h1>
        <p className="text-lg text-muted-foreground">
          Advanced Multi-Modal Intelligent RAG Platform with Hybrid Retrieval and Agentic
          Reasoning.
        </p>
      </div>

      <div
        className="flex flex-col gap-4 border bg-card p-6"
        style={{ borderRadius: "var(--radius-card)" }}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Development stack</span>
          <HealthBadge />
        </div>
        <ul className="grid grid-cols-2 gap-2 font-mono text-sm text-muted-foreground">
          <li>Frontend · Next.js :3000</li>
          <li>Backend · FastAPI :8000</li>
          <li>PostgreSQL :5432</li>
          <li>Redis :6379</li>
          <li>Qdrant :6333</li>
          <li>Neo4j :7474</li>
          <li>MinIO :9001</li>
          <li>Celery worker</li>
        </ul>
      </div>

      <p className="text-sm text-muted-foreground">
        The foundation is in place. Next: Phase 1 — Core Backend, Authentication &amp; Database.
      </p>
    </main>
  );
}
