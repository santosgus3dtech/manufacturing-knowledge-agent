export type MachineState = "printing" | "idle" | "attention" | "offline";
export type HealthState = "healthy" | "degraded" | "unavailable";

export interface Temperature {
  current: number | null;
  target: number | null;
}

export interface MachineJob {
  reference: string;
  part: string;
  material: string;
  progress_percent: number;
  remaining_minutes: number;
}

export interface Machine {
  id: string;
  name: string;
  process: "FDM" | "SLA";
  workspace_mm: string;
  state: MachineState;
  health: HealthState;
  status_message: string;
  nozzle: Temperature;
  bed: Temperature;
  job: MachineJob | null;
  last_seen: string;
}

export interface DashboardSummary {
  mode: string;
  machines: number;
  needs_attention: number;
  knowledge_chunks: number;
  citation_precision: number;
  retrieval_mrr: number;
}

export interface Citation {
  document_id: string;
  title: string;
  page: number;
  excerpt: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  strategy: string;
  results: Array<{
    chunk_id: string;
    document_id: string;
    title: string;
    section: string;
    page: number;
    domain: string;
    excerpt: string;
    score: number;
  }>;
}

export interface ToolTrace {
  id: string;
  tool: string;
  input_summary: string;
  result: "success" | "fallback" | "blocked";
  duration_ms: number;
  created_at: string;
}

export interface AskResponse {
  answer: string;
  confidence: number;
  provider: string;
  citations: Citation[];
  tools: ToolTrace[];
}

export interface QuoteRequest {
  material: string;
  part_weight_g: number;
  print_hours: number;
  labor_minutes: number;
  quantity: number;
  failure_rate_percent: number;
  margin_percent: number;
}

export interface QuoteBreakdown {
  material: string;
  quantity: number;
  material_cost: number;
  energy_cost: number;
  machine_cost: number;
  labor_cost: number;
  packaging_cost: number;
  risk_buffer: number;
  unit_cost: number;
  unit_price: number;
  total_price: number;
  currency: "USD";
}

export interface EvaluationResult {
  id: string;
  question: string;
  category: string;
  expected_document_ids: string[];
  retrieved_document_ids: string[];
  hit_at_3: boolean;
  reciprocal_rank: number;
}

export interface EvaluationSummary {
  cases: number;
  recall_at_3: number;
  mean_reciprocal_rank: number;
  citation_precision_target: number;
  results: EvaluationResult[];
}
