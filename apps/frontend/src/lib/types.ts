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
  chunking_strategy: string;
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

export interface AuditLog {
  id: string;
  actor_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  metadata_json: Record<string, unknown> | null;
  timestamp: string;
}

export interface UsageSummary {
  knowledge_bases: number;
  documents: number;
  experiments: number;
  audit_events: number;
}

export type RetrievalMode = "vector" | "graph" | "hybrid";

export interface StudioChunk {
  chunk_id: string;
  document_id: string;
  file_name: string;
  chunk_index: number;
  text: string;
  score: number;
  vector_score: number | null;
  lexical_score: number | null;
  fused_score: number | null;
}

export interface StudioTriple {
  source: string;
  relation: string;
  target: string;
}

export interface ExperimentMetrics {
  latency_ms: number;
  token_usage: number | null;
  score: number | null;
  retrieved_count: number;
  relationship_count: number;
}

export interface ExperimentResponse {
  run_id: string;
  retrieval_mode: RetrievalMode;
  answer: string;
  vector_results: StudioChunk[];
  graph_results: StudioTriple[];
  metrics: ExperimentMetrics;
  model: string;
  llm_configured: boolean;
  generation_error: string | null;
}

export interface EvaluationRun {
  id: string;
  knowledge_base_id: string | null;
  retrieval_mode: RetrievalMode;
  embedding_model: string;
  reranker: string | null;
  chunk_size: number | null;
  top_k: number;
  latency_ms: number;
  token_usage: number | null;
  score: number | null;
  created_at: string;
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

export type AgentTraceStep = { node: string } & Record<string, unknown>;

export interface AgentResponse {
  message_id: string;
  answer: string;
  trace: AgentTraceStep[];
  sources: ChatCitation[];
  confidence: number | null;
  needs_approval: boolean;
  model: string;
  llm_configured: boolean;
  generation_error: string | null;
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
