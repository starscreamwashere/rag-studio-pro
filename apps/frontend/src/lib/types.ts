export interface Role {
  id: string;
  name: string;
  permissions: string[];
}

export interface User {
  id: string;
  clerk_user_id: string;
  organization_id: string;
  email: string;
  full_name: string | null;
  role: Role;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export type IngestionStatus = "pending" | "processing" | "completed" | "failed";

export interface KnowledgeBase {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  embedding_model: string;
  retrieval_default: string;
  status: "active" | "syncing" | "failed" | "archived";
  created_at: string;
  document_count: number;
}

export interface Document {
  id: string;
  knowledge_base_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  ingestion_status: IngestionStatus;
  uploaded_at: string;
}

export interface GraphEntity {
  id: string | null;
  name: string;
  type: string | null;
  degree: number;
}

export interface GraphTriple {
  source: string;
  relation: string;
  target: string;
}

export interface GraphStats {
  entities: number;
  relationships: number;
}

export interface ChatCitation {
  index: number;
  document_id: string;
  file_name: string;
  score: number;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  citations: ChatCitation[] | null;
  confidence_score: number | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  knowledge_base_id: string | null;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface IngestionJob {
  id: string;
  document_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  current_step: string | null;
  progress_percent: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}
