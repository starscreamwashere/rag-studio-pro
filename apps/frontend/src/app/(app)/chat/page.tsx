"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { Globe, MessageSquare, Sparkles } from "lucide-react";
import { ChatInput } from "@/components/chat/chat-input";
import { ChatSidebar } from "@/components/chat/chat-sidebar";
import { MessageBubble } from "@/components/chat/message-bubble";
import { NewChatDialog } from "@/components/chat/new-chat-dialog";
import { TraceDrawer } from "@/components/chat/trace-drawer";
import { Button } from "@/components/ui/button";
import { streamChatMessage } from "@/lib/chat-stream";
import { useAgentMessage, useChatSession } from "@/lib/hooks";
import type { AgentResponse, ChatCitation } from "@/lib/types";
import { cn } from "@/lib/utils";

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
  const [agentMode, setAgentMode] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [agentResult, setAgentResult] = useState<AgentResponse | null>(null);
  const [lastQuery, setLastQuery] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: detail } = useChatSession(sessionId);
  const agentMsg = useAgentMessage(sessionId);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [detail?.messages, draft, agentResult]);

  async function send(content: string, allowWeb = false) {
    if (!sessionId || sending) return;
    setSending(true);
    setLastQuery(content);
    setAgentResult(null);
    setDraft({ user: content, assistant: "", citations: [], confidence: null, error: null });
    try {
      if (agentMode) {
        const res = await agentMsg.mutateAsync({ content, allow_web_search: allowWeb });
        setAgentResult(res);
      } else {
        const token = await getToken();
        await streamChatMessage(token, sessionId, content, {
          onMeta: (d) =>
            setDraft((p) => (p ? { ...p, citations: d.citations, confidence: d.confidence } : p)),
          onToken: (t) => setDraft((p) => (p ? { ...p, assistant: p.assistant + t } : p)),
          onError: (dt) => setDraft((p) => (p ? { ...p, error: dt } : p)),
        });
      }
    } catch {
      setDraft((p) => (p ? { ...p, error: "Something went wrong." } : p));
    } finally {
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
        onSelect={(id) => {
          setSessionId(id);
          setAgentResult(null);
        }}
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
              sources; Agent mode reasons over tools.
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
                      content={draft.assistant || (agentMode ? "Reasoning over tools…" : "")}
                      citations={draft.citations}
                      confidence={draft.confidence}
                      streaming={!draft.error}
                    />
                    {draft.error && <p className="text-sm text-destructive">{draft.error}</p>}
                  </>
                )}
                {agentResult && !draft && (
                  <>
                    <TraceDrawer trace={agentResult.trace} />
                    {agentResult.needs_approval && (
                      <div className="flex items-center justify-between gap-3 rounded-[var(--radius-card)] border border-[#f5c27a] bg-[#fdf3e3] px-4 py-3 text-sm">
                        <span className="flex items-center gap-2 text-[#9a6b1e]">
                          <Globe className="h-4 w-4" />
                          The agent wants to search the web to answer this.
                        </span>
                        <Button size="sm" onClick={() => send(lastQuery, true)}>
                          Approve search
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="mx-auto w-full max-w-3xl px-4 pt-2">
              <button
                onClick={() => setAgentMode((v) => !v)}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                  agentMode
                    ? "border-primary/40 bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-surface-2",
                )}
              >
                <Sparkles className="h-3.5 w-3.5" />
                Agent mode {agentMode ? "on" : "off"}
              </button>
            </div>
            <div className="mx-auto w-full max-w-3xl">
              <ChatInput onSend={(t) => send(t)} disabled={sending} />
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
