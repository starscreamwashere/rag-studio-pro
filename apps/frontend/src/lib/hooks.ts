"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, useApi } from "@/lib/api";
import type { Organization, User, Workspace } from "@/lib/types";

/** Current user. `data` is null when the user is authenticated but not onboarded. */
export function useMe() {
  const { request } = useApi();
  return useQuery({
    queryKey: ["me"],
    queryFn: async (): Promise<User | null> => {
      try {
        return await request<User>("/auth/me");
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) return null;
        throw err;
      }
    },
  });
}

export function useCurrentOrganization(enabled = true) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["organization", "current"],
    queryFn: () => request<Organization>("/organizations/current"),
    enabled,
  });
}

export function useWorkspaces(enabled = true) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: () => request<Workspace[]>("/workspaces"),
    enabled,
  });
}

export function useCreateOrganization() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string; workspace_name: string }) =>
      request<Organization>("/organizations", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["me"] }),
  });
}

export function useCreateWorkspace() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string; description?: string }) =>
      request<Workspace>("/workspaces", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workspaces"] }),
  });
}
