// Thin API client for the Project Health backend.
// Configure the base URL via VITE_API_BASE_URL (defaults to "/api").

export const API_BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") || "/api";

// Optional API key read from VITE_API_KEY env var
const API_KEY: string = (import.meta.env.VITE_API_KEY as string | undefined) || "";

export class ApiError extends Error {
  constructor(public status: number, message: string, public body?: unknown) {
    super(message);
  }
}

async function parseError(res: Response): Promise<ApiError> {
  let body: unknown = undefined;
  let message = `${res.status} ${res.statusText}`;
  try {
    const text = await res.text();
    if (text) {
      try {
        body = JSON.parse(text);
        const b = body as { error?: string; message?: string; detail?: string };
        message = b.error || b.message || b.detail || message;
      } catch {
        message = text.slice(0, 300);
      }
    }
  } catch {
    /* ignore */
  }
  return new ApiError(res.status, message, body);
}

/** Auth headers — includes X-Api-Key when configured via VITE_API_KEY */
function authHeaders(): Record<string, string> {
  return API_KEY ? { "X-Api-Key": API_KEY } : {};
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as T;
}

export async function apiPostJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json", ...authHeaders() },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as T;
}

export async function apiUpload<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: form,
  });
  if (!res.ok) throw await parseError(res);
  return (await res.json()) as T;
}

export function fileDownloadUrl(path: string): string {
  return `${API_BASE}/files?path=${encodeURIComponent(path)}`;
}

// ─── Types ────────────────────────────────────────────────────────────────────

export type RagStatus = "Red" | "Amber" | "Green" | string;

export interface Snapshot {
  snapshot_id: number;
  project_id: number;
  project_name: string;
  rag_status: RagStatus;
  rag_score: number;
  confidence: string;
  data_quality_score: number;
  weekly_markdown_path?: string | null;
  weekly_json_path?: string | null;
}

export interface AnalyzeResponse {
  run_date: string;
  snapshots: Snapshot[];
}

export interface PortfolioProject {
  project_id: number;
  snapshot_id: number;
  name: string;
  source_file?: string | null;
  project_manager?: string | null;
  run_date: string;
  rag_status: RagStatus;
  rag_score: number;
  confidence: string;
  data_quality_score: number;
  source_schedule_health: RagStatus;
  project_stage?: string | null;
  rag_flip_alert?: string | null;
  weekly_markdown_path?: string | null;
  weekly_json_path?: string | null;
}

export interface PortfolioResponse {
  projects: PortfolioProject[];
}

export interface Signal {
  signal_name: string;
  weight: number;
  raw_value: number | string | null;
  score: number;
  weighted_score: number;
  evidence: string[] | string;
  triggered_override: boolean;
}

export interface SnapshotDetail {
  snapshot_id: number;
  project_name: string;
  run_date: string;
  rag_status: RagStatus;
  rag_score: number;
  confidence: string;
  data_quality_score: number;
  source_schedule_health: RagStatus;
  reasons: string[];
  top_risks: string[];
  recommendations: string[];
  caveats: string[];
  signals: Signal[];
  all_task_columns: string[];
  project_id?: number;
  executive_summary?: string | null;
  sentiment_summary?: string | null;
  risk_themes?: string[];
  agent_mode?: string;
  rag_flip_alert?: string | null;
}

export interface SnapshotDetailResponse {
  snapshot: SnapshotDetail;
}

export interface TaskRow {
  source_row: number;
  parent_source_row: number | null;
  level: number;
  task_name: string;
  phase_milestone: string | null;
  status: string | null;
  percent_complete: number | null;
  start_date: string | null;
  end_date: string | null;
  baseline_start: string | null;
  baseline_finish: string | null;
  variance: number | null;
  total_float: number | null;
  critical: boolean;
  on_hold: boolean;
  owner: string | null;
  assigned_to: string | null;
  status_comment: string | null;
  source_schedule_health: RagStatus;
  raw_data?: Record<string, unknown>;
}

export interface TasksResponse {
  tasks: TaskRow[];
}

export interface CommentRow {
  source_row: number;
  referenced_row: number | null;
  comment_text: string;
  author: string | null;
  created_at_source: string | null;
}

export interface CommentsResponse {
  comments: CommentRow[];
}

export interface MonthlySynthesisResponse {
  deck_path: string;
}

export interface AskResponse {
  rows: Array<Record<string, unknown>>;
}

/** One data point in a project's historical RAG score trend */
export interface TrendPoint {
  snapshot_id: number;
  run_date: string;
  rag_status: RagStatus;
  rag_score: number;
  confidence: string;
  data_quality_score: number;
  source_schedule_health?: string | null;
  project_stage?: string | null;
  rag_flip_alert?: string | null;
}

export interface TrendResponse {
  project_id: number;
  trend: TrendPoint[];
}

// ─── API surface ──────────────────────────────────────────────────────────────

export const api = {
  analyze: (files: File[], runDate?: string) => {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    if (runDate) fd.append("run_date", runDate);
    return apiUpload<AnalyzeResponse>("/analyze", fd);
  },
  portfolio: () => apiGet<PortfolioResponse>("/projects/latest"),
  snapshot: (id: number | string) => apiGet<SnapshotDetailResponse>(`/snapshots/${id}`),
  tasks: (id: number | string) => apiGet<TasksResponse>(`/snapshots/${id}/tasks`),
  comments: (id: number | string) => apiGet<CommentsResponse>(`/snapshots/${id}/comments`),
  monthlySynthesis: () => apiPostJSON<MonthlySynthesisResponse>("/monthly-synthesis", {}),
  ask: (question: string) => apiPostJSON<AskResponse>("/ask", { question }),
  trend: (projectId: number | string) => apiGet<TrendResponse>(`/projects/${projectId}/trend`),
  exportPdfUrl: (snapshotId: number | string) => `${API_BASE}/snapshots/${snapshotId}/pdf`,
  deleteSnapshot: (id: number | string) => {
    return fetch(`${API_BASE}/snapshots/${id}`, {
      method: "DELETE",
      headers: { ...authHeaders() },
    }).then(async (res) => {
      if (!res.ok) throw await parseError(res);
      return res.json() as Promise<{ status: string; message: string }>;
    });
  },
};