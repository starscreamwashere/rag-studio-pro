import { PageHeader } from "@/components/app/page-header";

/** Placeholder for routes whose functionality ships in a later phase. */
export function ComingSoon({
  title,
  phase,
  description,
}: {
  title: string;
  phase: number;
  description: string;
}) {
  return (
    <>
      <PageHeader title={title} description={description} />
      <div className="flex flex-col items-center justify-center gap-2 px-8 py-24 text-center">
        <span className="rounded-full bg-surface-2 px-3 py-1 font-mono text-xs text-muted-foreground">
          Ships in Phase {phase}
        </span>
        <p className="max-w-md text-sm text-muted-foreground">
          This area is part of the phased roadmap and isn’t built yet.
        </p>
      </div>
    </>
  );
}
