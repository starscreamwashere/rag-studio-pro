"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/app/sidebar";
import { useMe } from "@/lib/hooks";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data: user, isLoading, isError, error } = useMe();

  // Authenticated but no organization yet → send through onboarding.
  useEffect(() => {
    if (!isLoading && user === null) {
      router.replace("/onboarding");
    }
  }, [isLoading, user, router]);

  if (isLoading || user === null) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
        Loading…
      </div>
    );
  }

  if (isError || !user) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-2 px-6 text-center">
        <p className="font-medium">Couldn’t reach the API.</p>
        <p className="text-sm text-muted-foreground">{(error as Error)?.message}</p>
      </div>
    );
  }

  return (
    <div className="flex">
      <Sidebar user={user} />
      <main className="h-screen flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
