"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { useCreateOrganization, useMe } from "@/lib/hooks";

export default function OnboardingPage() {
  const router = useRouter();
  const { data: user, isLoading } = useMe();
  const createOrg = useCreateOrganization();

  const [orgName, setOrgName] = useState("");
  const [workspaceName, setWorkspaceName] = useState("Default Workspace");

  // Already onboarded → straight to the dashboard.
  useEffect(() => {
    if (!isLoading && user) router.replace("/dashboard");
  }, [isLoading, user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await createOrg.mutateAsync({ name: orgName, workspace_name: workspaceName });
    router.replace("/dashboard");
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md">
        <CardTitle>Set up your organization</CardTitle>
        <CardDescription>
          Create your organization and first workspace to get started.
        </CardDescription>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="org" className="text-sm font-medium">
              Organization name
            </label>
            <Input
              id="org"
              required
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              placeholder="Acme Inc."
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="workspace" className="text-sm font-medium">
              First workspace
            </label>
            <Input
              id="workspace"
              required
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              placeholder="Engineering"
            />
          </div>

          {createOrg.isError && (
            <p className="text-sm text-destructive">{(createOrg.error as Error).message}</p>
          )}

          <Button type="submit" size="lg" disabled={createOrg.isPending}>
            {createOrg.isPending ? "Creating…" : "Create organization"}
          </Button>
        </form>
      </Card>
    </main>
  );
}
