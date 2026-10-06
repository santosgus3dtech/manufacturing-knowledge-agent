import type {
  AskResponse,
  DashboardSummary,
  EvaluationSummary,
  Machine,
  QuoteBreakdown,
  QuoteRequest,
  SearchResponse,
  ToolTrace,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<DashboardSummary>("/api/dashboard"),
  machines: () => request<Machine[]>("/api/machines"),
  activity: () => request<ToolTrace[]>("/api/activity"),
  evaluations: () => request<EvaluationSummary>("/api/evaluations"),
  search: (query: string) => request<SearchResponse>(`/api/knowledge/search?q=${encodeURIComponent(query)}&top_k=5`),
  ask: (question: string) =>
    request<AskResponse>("/api/agent/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  quote: (payload: QuoteRequest) =>
    request<QuoteBreakdown>("/api/quotes/estimate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
