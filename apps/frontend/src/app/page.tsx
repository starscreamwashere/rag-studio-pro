import Link from "next/link";
import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

const FEATURES = [
  ["Multi-modal ingestion", "PDFs, docs, data, and connectors into one knowledge base."],
  ["Hybrid retrieval", "Vector + graph retrieval with reranking and score fusion."],
  ["Experimentation studio", "Tune chunking, embeddings, and retrieval in real time."],
  ["Agentic reasoning", "An agent that selects tools and explains every answer."],
];

export default function Landing() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6">
      <header className="flex items-center justify-between py-6">
        <span className="font-semibold tracking-tight">RAG Studio Pro</span>
        <nav className="flex items-center gap-2">
          <SignedOut>
            <Link href="/sign-in">
              <Button variant="ghost" size="sm">
                Login
              </Button>
            </Link>
            <Link href="/sign-up">
              <Button size="sm">Sign Up</Button>
            </Link>
          </SignedOut>
          <SignedIn>
            <Link href="/dashboard">
              <Button size="sm">Open dashboard</Button>
            </Link>
          </SignedIn>
        </nav>
      </header>

      <section className="flex flex-1 flex-col justify-center gap-8 py-16">
        <div className="flex max-w-2xl flex-col gap-4">
          <h1 className="text-5xl font-semibold leading-tight tracking-tight">
            The intelligent RAG platform for production knowledge.
          </h1>
          <p className="text-lg text-muted-foreground">
            Advanced Multi-Modal Intelligent RAG Platform with Hybrid Retrieval and Agentic
            Reasoning.
          </p>
          <div className="flex gap-3 pt-2">
            <SignedOut>
              <Link href="/sign-up">
                <Button size="lg">Get started</Button>
              </Link>
              <Link href="/sign-in">
                <Button size="lg" variant="outline">
                  Login
                </Button>
              </Link>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard">
                <Button size="lg">Go to dashboard</Button>
              </Link>
            </SignedIn>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {FEATURES.map(([title, desc]) => (
            <div key={title} className="rounded-[var(--radius-card)] border bg-card p-5">
              <h3 className="font-medium">{title}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
