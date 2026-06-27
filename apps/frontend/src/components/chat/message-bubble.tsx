import { SourceCards } from "@/components/chat/source-cards";
import type { ChatCitation } from "@/lib/types";
import { cn } from "@/lib/utils";

export function MessageBubble({
  role,
  content,
  citations,
  confidence,
  streaming,
}: {
  role: string;
  content: string;
  citations?: ChatCitation[] | null;
  confidence?: number | null;
  streaming?: boolean;
}) {
  const isUser = role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-[var(--radius-card)] px-4 py-3 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "border bg-card",
        )}
      >
        <p className="whitespace-pre-wrap">
          {content}
          {streaming && <span className="ml-0.5 animate-pulse">▍</span>}
        </p>
        {!isUser && citations && citations.length > 0 && <SourceCards citations={citations} />}
        {!isUser && confidence != null && !streaming && (
          <p className="mt-2 text-xs text-muted-foreground">
            Confidence {(confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>
    </div>
  );
}
