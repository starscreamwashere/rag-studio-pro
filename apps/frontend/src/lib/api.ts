"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_V1 = `${API_URL}/api/v1`;

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

/** Returns an authenticated `request` helper that attaches the Clerk token. */
export function useApi() {
  const { getToken } = useAuth();

  const request = useCallback(
    async <T>(path: string, init: RequestInit = {}): Promise<T> => {
      const token = await getToken();
      // Let the browser set the multipart boundary for FormData uploads.
      const isFormData = init.body instanceof FormData;
      const res = await fetch(`${API_V1}${path}`, {
        ...init,
        headers: {
          ...(isFormData ? {} : { "Content-Type": "application/json" }),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...init.headers,
        },
      });

      if (!res.ok) {
        let detail = res.statusText;
        try {
          const body = await res.json();
          detail = body.detail ?? detail;
        } catch {
          // non-JSON error body
        }
        throw new ApiError(res.status, detail);
      }

      if (res.status === 204) return undefined as T;
      return (await res.json()) as T;
    },
    [getToken],
  );

  return { request };
}
