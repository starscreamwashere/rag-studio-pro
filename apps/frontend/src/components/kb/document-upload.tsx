"use client";

import { useRef, useState } from "react";
import { Upload } from "lucide-react";
import { ApiError } from "@/lib/api";
import { useUploadDocument } from "@/lib/hooks";
import { cn } from "@/lib/utils";

const ACCEPT = ".pdf,.docx,.txt,.md,.csv,.json,.ppt,.pptx,.html,.htm";

export function DocumentUpload({ kbId }: { kbId: string }) {
  const upload = useUploadDocument(kbId);
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  async function handleFiles(files: FileList | null) {
    if (!files?.length) return;
    setError(null);
    for (const file of Array.from(files)) {
      try {
        await upload.mutateAsync(file);
      } catch (e) {
        setError(e instanceof ApiError ? e.detail : "Upload failed");
      }
    }
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex w-full flex-col items-center gap-2 rounded-[var(--radius-card)] border border-dashed p-8 text-center transition-colors",
          dragging ? "border-primary bg-primary/5" : "hover:bg-surface-2",
        )}
      >
        <Upload className="h-6 w-6 text-muted-foreground" />
        <span className="text-sm font-medium">
          {upload.isPending ? "Uploading…" : "Drop a file or click to upload"}
        </span>
        <span className="text-xs text-muted-foreground">
          PDF, DOCX, PPT, TXT, CSV, JSON, HTML · up to 50 MB
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
    </div>
  );
}
