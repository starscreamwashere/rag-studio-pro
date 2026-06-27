import type { ChatCitation } from "@/lib/types";

const API_V1 = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;

export interface StreamHandlers {
  onMeta?: (data: { citations: ChatCitation[]; confidence: number | null }) => void;
  onToken?: (text: string) => void;
  onDone?: (data: { message_id: string }) => void;
  onError?: (detail: string) => void;
}

/** POST a chat message and consume the SSE stream (fetch + ReadableStream). */
export async function streamChatMessage(
  token: string | null,
  sessionId: string,
  content: string,
  h: StreamHandlers,
): Promise<void> {
  const res = await fetch(`${API_V1}/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ content }),
  });

  if (!res.ok || !res.body) {
    let detail = `Request failed (HTTP ${res.status})`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* non-JSON */
    }
    h.onError?.(detail);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) >= 0) {
      const block = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      handleBlock(block, h);
    }
  }
}

function handleBlock(block: string, h: StreamHandlers): void {
  let event = "message";
  let data = "";
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data = line.slice(5).trim();
  }
  if (!data) return;
  const parsed = JSON.parse(data);
  if (event === "meta") h.onMeta?.(parsed);
  else if (event === "token") h.onToken?.(parsed.text);
  else if (event === "done") h.onDone?.(parsed);
  else if (event === "error") h.onError?.(parsed.detail);
}
