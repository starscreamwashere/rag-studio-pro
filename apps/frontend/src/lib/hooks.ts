"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, useApi } from "@/lib/api";
import type {
  ChatSession,
  ChatSessionDetail,
  Document,
  IngestionJob,
  KnowledgeBase,
  Organization,
  User,
  Workspace,
} from "@/lib/types";

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

// ---- Knowledge bases --------------------------------------------------------

export function useKnowledgeBases() {
  const { request } = useApi();
  return useQuery({
    queryKey: ["knowledge-bases"],
    queryFn: () => request<KnowledgeBase[]>("/knowledge-bases"),
  });
}

export function useKnowledgeBase(id: string) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["knowledge-bases", id],
    queryFn: () => request<KnowledgeBase>(`/knowledge-bases/${id}`),
  });
}

export function useCreateKnowledgeBase() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { workspace_id: string; name: string; description?: string }) =>
      request<KnowledgeBase>("/knowledge-bases", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["knowledge-bases"] }),
  });
}

export function useDeleteKnowledgeBase() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      request<void>(`/knowledge-bases/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["knowledge-bases"] }),
  });
}

// ---- Documents & ingestion jobs --------------------------------------------

export function useDocuments(kbId: string) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["knowledge-bases", kbId, "documents"],
    queryFn: () => request<Document[]>(`/knowledge-bases/${kbId}/documents`),
  });
}

export function useUploadDocument(kbId: string) {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return request<Document>(`/knowledge-bases/${kbId}/documents`, {
        method: "POST",
        body: form,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["knowledge-bases", kbId, "documents"] });
      qc.invalidateQueries({ queryKey: ["knowledge-bases"] });
    },
  });
}

// ---- Chat -------------------------------------------------------------------

export function useChatSessions() {
  const { request } = useApi();
  return useQuery({
    queryKey: ["chat-sessions"],
    queryFn: () => request<ChatSession[]>("/chat/sessions"),
  });
}

export function useChatSession(id: string | null) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["chat-session", id],
    queryFn: () => request<ChatSessionDetail>(`/chat/sessions/${id}`),
    enabled: !!id,
  });
}

export function useCreateChatSession() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { knowledge_base_id: string; title?: string }) =>
      request<ChatSession>("/chat/sessions", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chat-sessions"] }),
  });
}

export function useDeleteChatSession() {
  const { request } = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => request<void>(`/chat/sessions/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chat-sessions"] }),
  });
}

/** Polls the latest ingestion job while it is still running. */
export function useDocumentJob(documentId: string, active: boolean) {
  const { request } = useApi();
  return useQuery({
    queryKey: ["documents", documentId, "job"],
    queryFn: async (): Promise<IngestionJob | null> => {
      try {
        return await request<IngestionJob>(`/documents/${documentId}/job`);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) return null;
        throw err;
      }
    },
    enabled: active,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 1500;
    },
  });
}
