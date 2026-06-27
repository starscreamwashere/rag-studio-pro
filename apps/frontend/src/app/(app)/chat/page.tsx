"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { MessageSquare } from "lucide-react";
import { ChatInput } from "@/components/chat/chat-input";
import { ChatSidebar } from "@/components/chat/chat-sidebar";
import { MessageBubble } from "@/components/chat/message-bubble";
import { NewChatDialog } from "@/components/chat/new-chat-dialog";
import { Button } from "@/components/ui/button";
import { streamChatMessage } from "@/lib/chat-stream";
import { useChatSession } from "@/lib/hooks";
import type { ChatCitation } from "@/lib/types";

interface Draft {
  user: string;
  assistant: string;
  citations: ChatCitation[];
  confidence: number | null;
  error: string | null;
}

export default function ChatPage() {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [newOpen, setNewOpen] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: detail } = useChatSession(sessionId);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [detail?.messages, draft]);

  async function handleSend(content: string) {
    if (!sessionId || sending) return;
    setSending(true);
    setDraft({ user: content, assistant: "", citations: [], confidence: null, error: null });
    try {
      const token = await getToken();
      await streamChatMessage(token, sessionId, content, {
        onMeta: (d) =>
          setDraft((p) => (p ? { ...p, citations: d.citations, confidence: d.confidence } : p)),
        onToken: (t) => setDraft((p) => (p ? { ...p, assistant: p.assistant + t } : p)),
        onError: (dt) => setDraft((p) => (p ? { ...p, error: dt } : p)),
      });
    } catch {
      setDraft((p) => (p ? { ...p, error: "Connection lost." } : p));
    } finally {
      // Refetch persisted history, then drop the in-flight draft (no flash).
      await qc.invalidateQueries({ queryKey: ["chat-session", sessionId] });
      qc.invalidateQueries({ queryKey: ["chat-sessions"] });
      setDraft(null);
      setSending(false);
    }
  }

  return (
    <div className="flex h-full">
      <ChatSidebar
        selectedId={sessionId}
        onSelect={setSessionId}
        onNew={() => setNewOpen(true)}
        onDeleted={(id) => {
          if (id === sessionId) setSessionId(null);
        }}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {!sessionId ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
            <MessageSquare className="h-10 w-10 text-muted-foreground" />
            <p className="text-lg font-medium">Enterprise knowledge assistant</p>
            <p className="max-w-sm text-sm text-muted-foreground">
              Start a conversation grounded in one of your knowledge bases. Answers cite their
              sources.
            </p>
            <Button onClick={() => setNewOpen(true)}>Start a new chat</Button>
          </div>
        ) : (
          <>
            <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto p-6">
              <div className="mx-auto flex max-w-3xl flex-col gap-4">
                {detail?.messages.map((m) => (
                  <MessageBubble
                    key={m.id}
                    role={m.role}
                    content={m.content}
                    citations={m.citations}
                    confidence={m.confidence_score}
                  />
                ))}
                {draft && (
                  <>
                    <MessageBubble role="user" content={draft.user} />
                    <MessageBubble
                      role="assistant"
                      content={draft.assistant}
                      citations={draft.citations}
                      confidence={draft.confidence}
                      streaming={!draft.error}
                    />
                    {draft.error && <p className="text-sm text-destructive">{draft.error}</p>}
                  </>
                )}
              </div>
            </div>
            <div className="mx-auto w-full max-w-3xl">
              <ChatInput onSend={handleSend} disabled={sending} />
            </div>
          </>
        )}
      </div>

      <NewChatDialog
        open={newOpen}
        onClose={() => setNewOpen(false)}
        onCreated={(id) => setSessionId(id)}
      />
    </div>
  );
}
