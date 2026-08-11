import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type CommentRow, type Signal, type TaskRow, type TrendPoint } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { RagBadge } from "@/components/rag-badge";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AlertTriangle, ArrowLeft, Bot, Brain, Download, FileDown, Loader2, MessageSquare, TrendingUp, Trash2, GitBranch } from "lucide-react";
import { useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  LineChart,
  Line,
  ReferenceLine,
  Legend,
} from "recharts";

export const Route = createFileRoute("/_authenticated/projects/$snapshotId")({
  component: SnapshotDetail,
});

function SnapshotDetail() {
  const { snapshotId } = Route.useParams();
  const navigate = useNavigate();
  const detail = useQuery({
    queryKey: ["snapshot", snapshotId],
    queryFn: () => api.snapshot(snapshotId),
  });
  const tasks = useQuery({
    queryKey: ["snapshot-tasks", snapshotId],
    queryFn: () => api.tasks(snapshotId),
  });
  const comments = useQuery({
    queryKey: ["snapshot-comments", snapshotId],
    queryFn: () => api.comments(snapshotId),
  });
  const portfolio = useQuery({
    queryKey: ["portfolio"],
    queryFn: api.portfolio,
  });

  const s = detail.data?.snapshot;
  const allProjects = portfolio.data?.projects ?? [];

  // Trend data — load once we know the project_id
  const trend = useQuery({
    queryKey: ["trend", s?.project_id],
    queryFn: () => api.trend(s!.project_id!),
    enabled: !!s?.project_id,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <Link to="/portfolio" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to portfolio
        </Link>
      </div>

      {detail.isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground py-10 justify-center">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading snapshot…
        </div>
      ) : detail.isError ? (
        <ErrorState message={(detail.error as Error).message} onRetry={() => detail.refetch()} />
      ) : !s ? (
        <EmptyState title="Snapshot not found" />
      ) : (
        <>
          {/* RAG flip alert banner */}
          {s.rag_flip_alert ? (
            <div className="flex items-center gap-2 rounded-lg border border-rag-red/40 bg-rag-red/10 px-4 py-2.5 text-sm font-medium text-rag-red">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              {s.rag_flip_alert}
            </div>
          ) : null}

          <Card>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <CardTitle className="text-xl">{s.project_name}</CardTitle>
                    {allProjects.length > 1 && (
                      <Select
                        value={String(snapshotId)}
                        onValueChange={(val) => {
                          navigate({ to: "/projects/$snapshotId", params: { snapshotId: val } });
                        }}
                      >
                        <SelectTrigger className="w-[180px] h-7 text-xs border-muted-foreground/30">
                          <SelectValue placeholder="Switch Project" />
                        </SelectTrigger>
                        <SelectContent>
                          {allProjects.map((p) => (
                            <SelectItem key={p.snapshot_id} value={String(p.snapshot_id)}>
                              {p.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                  <CardDescription>Run date: {s.run_date}</CardDescription>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <RagBadge status={s.rag_status} />
                  <Badge variant="outline">Score {s.rag_score?.toFixed?.(1) ?? "—"}</Badge>
                  <Badge variant="outline">Confidence {s.confidence}</Badge>
                  <Badge variant="outline">DQ {s.data_quality_score?.toFixed?.(1) ?? "—"}</Badge>
                  {/* AI Analysis badge — only shows if LLM ran, no provider name displayed */}
                  {s.agent_mode && s.agent_mode !== "offline" ? (
                    <Badge className="gap-1 bg-emerald-500/10 text-emerald-700 border-emerald-500/30">
                      <Bot className="h-3 w-3" /> AI Powered
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="gap-1">
                      <Brain className="h-3 w-3" />Rule Engine
                    </Badge>
                  )}
                  {/* PDF Export button */}
                  <button
                    onClick={() => window.open(api.exportPdfUrl(snapshotId), "_blank")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border/60 bg-background px-3 py-1.5 text-xs font-medium hover:bg-muted transition-colors ml-1 cursor-pointer"
                  >
                    <FileDown className="h-3.5 w-3.5" /> Export PDF
                  </button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/30 ml-1"
                    onClick={async () => {
                      if (confirm(`Are you sure you want to delete the snapshot for "${s.project_name}"?`)) {
                        try {
                          await api.deleteSnapshot(snapshotId);
                          navigate({ to: "/portfolio" });
                        } catch (err) {
                          alert(err instanceof Error ? err.message : "Failed to delete snapshot");
                        }
                      }
                    }}
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-1" /> Delete
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                <MetaBlock label="Agent-derived RAG"><RagBadge status={s.rag_status} /></MetaBlock>
                <MetaBlock label="Source schedule health"><RagBadge status={s.source_schedule_health} /></MetaBlock>
              </div>
            </CardContent>
          </Card>

          {/* LLM Agent Insights panel — only visible when agent ran */}
          {(s.executive_summary || s.sentiment_summary || (s.risk_themes && s.risk_themes.length > 0)) ? (
            <AgentInsightsPanel
              executiveSummary={s.executive_summary}
              sentimentSummary={s.sentiment_summary}
              riskThemes={s.risk_themes ?? []}
              agentMode={s.agent_mode}
            />
          ) : null}

          <Tabs defaultValue="reasoning">
            <TabsList className="flex-wrap h-auto">
              <TabsTrigger value="reasoning">Why this status</TabsTrigger>
              <TabsTrigger value="signals">Signals</TabsTrigger>
              <TabsTrigger value="tasks">Task evidence</TabsTrigger>
              <TabsTrigger value="gantt">Gantt Chart</TabsTrigger>
              <TabsTrigger value="trend">Trend</TabsTrigger>
              <TabsTrigger value="comments">Comments</TabsTrigger>
              <TabsTrigger value="attributes">Preserved attributes</TabsTrigger>
            </TabsList>

            <TabsContent value="reasoning" className="mt-4 space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <ListCard title="Reasons" items={s.reasons} empty="No reasoning provided." />
                <TopRisksCard items={s.top_risks} />
                <ListCard title="Recommended actions" items={s.recommendations} empty="No recommendations returned." />
                <ListCard title="Data caveats" items={s.caveats} empty="No caveats." />
              </div>
            </TabsContent>

            <TabsContent value="signals" className="mt-4 space-y-4">
              <SignalsView signals={s.signals} />
            </TabsContent>

            <TabsContent value="tasks" className="mt-4">
              {tasks.isLoading ? (
                <Loading label="Loading tasks…" />
              ) : tasks.isError ? (
                <ErrorState message={(tasks.error as Error).message} onRetry={() => tasks.refetch()} />
              ) : (
                <TaskTable tasks={tasks.data?.tasks ?? []} />
              )}
            </TabsContent>

            <TabsContent value="comments" className="mt-4">
              {comments.isLoading ? (
                <Loading label="Loading comments…" />
              ) : comments.isError ? (
                <ErrorState message={(comments.error as Error).message} onRetry={() => comments.refetch()} />
              ) : (
                <CommentTable comments={comments.data?.comments ?? []} />
              )}
            </TabsContent>

            <TabsContent value="attributes" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Preserved workbook attributes</CardTitle>
                  <CardDescription>All columns kept from the source workbook.</CardDescription>
                </CardHeader>
                <CardContent>
                  {s.all_task_columns?.length ? (
                    <div className="flex flex-wrap gap-1.5">
                      {s.all_task_columns.map((c) => (
                        <Badge key={c} variant="secondary" className="font-mono text-xs">{c}</Badge>
                      ))}
                    </div>
                  ) : (
                    <EmptyState title="No column list returned" />
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* ── Trend Tab ────────────────────────────────────────────── */}
            <TabsContent value="trend" className="mt-4">
              {trend.isLoading ? (
                <Loading label="Loading trend data…" />
              ) : trend.isError ? (
                <ErrorState message={(trend.error as Error).message} onRetry={() => trend.refetch()} />
              ) : (
                <TrendChart points={trend.data?.trend ?? []} currentSnapshotId={Number(snapshotId)} />
              )}
            </TabsContent>

            {/* ── Gantt Tab ────────────────────────────────────────────── */}
            <TabsContent value="gantt" className="mt-4">
              {tasks.isLoading ? (
                <Loading label="Loading tasks for Gantt…" />
              ) : tasks.isError ? (
                <ErrorState message={(tasks.error as Error).message} onRetry={() => tasks.refetch()} />
              ) : (
                <GanttChart tasks={tasks.data?.tasks ?? []} />
              )}
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}

function MetaBlock({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-md border border-border/60 p-3">
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-1.5">{children}</div>
    </div>
  );
}

function AgentInsightsPanel({
  executiveSummary,
  sentimentSummary,
  riskThemes,
  agentMode,
}: {
  executiveSummary?: string | null;
  sentimentSummary?: string | null;
  riskThemes: string[];
  agentMode?: string;
}) {
  const isLlm = agentMode && agentMode !== "offline";
  return (
    <Card className="border-primary/30">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Bot className="h-4 w-4 text-primary" />
          AI Agent Insights
          <Badge variant="outline" className="ml-auto text-xs">
            {isLlm ? "AI Powered" : "Rule Engine"}
          </Badge>
        </CardTitle>
        <CardDescription className="text-xs">
          {isLlm
            ? "The LLM agent analysed computed signals and comment evidence to produce this narrative."
            : "No API key configured — rule engine generated these summaries deterministically."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {executiveSummary ? (
          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Executive Summary</div>
            <p className="text-sm leading-relaxed">{executiveSummary}</p>
          </div>
        ) : null}

        {sentimentSummary ? (
          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Stakeholder Sentiment</div>
            <p className="text-sm leading-relaxed text-muted-foreground">{sentimentSummary}</p>
          </div>
        ) : null}

        {riskThemes.length > 0 ? (
          <div>
            <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5" /> Risk Themes
            </div>
            <div className="flex flex-wrap gap-2">
              {riskThemes.map((theme, i) => (
                <Badge key={i} variant="secondary" className="text-xs">{theme}</Badge>
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Loading({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 justify-center py-10 text-sm text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" /> {label}
    </div>
  );
}

function TopRisksCard({ items }: { items?: string[] }) {
  /** Parse a raw risk string like:
   *  "Row 14 | task_name: Design Phase | status: Not Started | health: Red | float: -3d | Comp: 0%"
   *  or any free-text risk into structured chips + message.
   */
  function parseRisk(raw: string) {
    // Try structured pipe-delimited format
    if (raw.includes("|")) {
      const parts = raw.split("|").map((p) => p.trim()).filter(Boolean);
      // First part often is "Row N" or project name
      const rowPart = parts[0];
      const fields: { label: string; value: string; highlight?: boolean }[] = [];
      for (const part of parts.slice(1)) {
        const colonIdx = part.indexOf(":");
        if (colonIdx !== -1) {
          const label = part.slice(0, colonIdx).trim();
          const value = part.slice(colonIdx + 1).trim();
          const isRisk =
            value.toLowerCase() === "red" ||
            (label.toLowerCase() === "float" && value.startsWith("-")) ||
            (label.toLowerCase() === "comp" && value === "0%");
          fields.push({ label, value, highlight: isRisk });
        } else {
          fields.push({ label: "", value: part });
        }
      }
      return { rowPart, fields, freeText: null };
    }
    // Free-text risk description — detect snake_case and clean it
    const cleaned = raw
      .replace(/_/g, " ")
      .replace(/\brag\b/gi, "RAG")
      .replace(/\bpct\b/gi, "%")
      .replace(/\s{2,}/g, " ")
      .trim();
    return { rowPart: null, fields: [], freeText: cleaned };
  }

  function severityBadge(value: string) {
    const v = value.toLowerCase();
    if (v === "red") return "bg-red-500/10 text-red-600 border-red-500/30";
    if (v === "amber" || v === "yellow") return "bg-amber-500/10 text-amber-600 border-amber-500/30";
    if (v === "green") return "bg-emerald-500/10 text-emerald-600 border-emerald-500/30";
    if (v.startsWith("-")) return "bg-red-500/10 text-red-600 border-red-500/30";
    return "bg-muted text-muted-foreground border-border";
  }

  if (!items?.length) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-rag-red" /> Top Risks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No top risks flagged.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-rag-red" /> Top Risks
          <span className="ml-auto rounded-full bg-rag-red/10 text-rag-red text-xs font-bold px-2 py-0.5">
            {items.length}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="space-y-3">
          {items.map((raw, i) => {
            const { rowPart, fields, freeText } = parseRisk(raw);
            return (
              <li key={i} className="rounded-lg border border-border/60 bg-muted/20 px-3 py-2.5 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-rag-red/15 text-rag-red text-[10px] font-bold shrink-0">
                    {i + 1}
                  </span>
                  {rowPart && (
                    <span className="text-xs font-semibold text-foreground">{rowPart}</span>
                  )}
                  {freeText && (
                    <span className="text-sm leading-snug">{freeText}</span>
                  )}
                </div>
                {fields.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pl-7">
                    {fields.map((f, fi) => (
                      <span
                        key={fi}
                        className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[11px] font-medium ${f.highlight ? severityBadge(f.value) : "bg-muted/60 text-muted-foreground border-border/60"}`}
                      >
                        {f.label && <span className="opacity-60">{f.label}:</span>}
                        <span>{f.value}</span>
                      </span>
                    ))}
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}

function ListCard({ title, items, empty, icon }: { title: string; items?: string[]; empty: string; icon?: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2">{icon}{title}</CardTitle></CardHeader>
      <CardContent>
        {items?.length ? (
          <ul className="space-y-1.5 text-sm">
            {items.map((r, i) => (
              <li key={i} className="flex gap-2"><span className="text-muted-foreground">•</span> {r}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">{empty}</p>
        )}
      </CardContent>
    </Card>
  );
}


function SignalsView({ signals }: { signals: Signal[] }) {
  if (!signals?.length) return <EmptyState title="No signal breakdown returned by backend." />;
  const chartData = signals.map((s) => ({
    name: s.signal_name,
    score: Number(s.score) || 0,
    weighted: Number(s.weighted_score) || 0,
  }));
  return (
    <>
      <Card>
        <CardHeader><CardTitle className="text-sm">Signal weighted scores</CardTitle></CardHeader>
        <CardContent style={{ height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis type="category" dataKey="name" stroke="var(--muted-foreground)" fontSize={11} width={140} />
              <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--popover-foreground)" }} />
              <Bar dataKey="weighted" fill="var(--primary)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <div className="grid gap-3 md:grid-cols-2">
        {signals.map((sig) => (
          <Card key={sig.signal_name}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center justify-between">
                {sig.signal_name}
                {sig.triggered_override ? <Badge className="bg-rag-red text-rag-red-foreground">Override</Badge> : null}
              </CardTitle>
              <CardDescription className="text-xs">
                Weight {sig.weight} · Score {sig.score} · Weighted {sig.weighted_score}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-muted-foreground mb-1">Raw value: <span className="font-mono">{String(sig.raw_value ?? "—")}</span></div>
              {Array.isArray(sig.evidence) ? (
                <ul className="space-y-1 text-sm">
                  {sig.evidence.map((e, i) => <li key={i} className="flex gap-2"><span className="text-muted-foreground">•</span>{e}</li>)}
                </ul>
              ) : sig.evidence ? (
                <p className="text-sm">{sig.evidence}</p>
              ) : (
                <p className="text-sm text-muted-foreground">No evidence provided.</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  );
}

function TaskTable({ tasks }: { tasks: TaskRow[] }) {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");
  const [health, setHealth] = useState("all");
  const [critical, setCritical] = useState(false);
  const [onHold, setOnHold] = useState(false);
  const [negFloat, setNegFloat] = useState(false);

  const statuses = useMemo(() => Array.from(new Set(tasks.map((t) => t.status).filter(Boolean))) as string[], [tasks]);

  const filtered = tasks.filter((t) => {
    if (q && !t.task_name?.toLowerCase().includes(q.toLowerCase())) return false;
    if (status !== "all" && t.status !== status) return false;
    if (health !== "all" && (t.source_schedule_health ?? "").toLowerCase() !== health) return false;
    if (critical && !t.critical) return false;
    if (onHold && !t.on_hold) return false;
    if (negFloat && !(typeof t.total_float === "number" && t.total_float < 0)) return false;
    return true;
  });

  if (!tasks.length) return <EmptyState title="No task evidence returned by backend." />;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Task evidence</CardTitle>
        <CardDescription>Source rows are preserved for auditability.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-2 md:grid-cols-[1fr_180px_180px]">
          <Input placeholder="Search task name…" value={q} onChange={(e) => setQ(e.target.value)} />
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger><SelectValue placeholder="Status" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              {statuses.map((st) => <SelectItem key={st} value={st}>{st}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={health} onValueChange={setHealth}>
            <SelectTrigger><SelectValue placeholder="Schedule health" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All health</SelectItem>
              <SelectItem value="red">Red</SelectItem>
              <SelectItem value="amber">Amber</SelectItem>
              <SelectItem value="green">Green</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-wrap gap-4 text-sm">
          <label className="flex items-center gap-2"><Checkbox checked={critical} onCheckedChange={(v) => setCritical(!!v)} /> Critical only</label>
          <label className="flex items-center gap-2"><Checkbox checked={onHold} onCheckedChange={(v) => setOnHold(!!v)} /> On hold only</label>
          <label className="flex items-center gap-2"><Checkbox checked={negFloat} onCheckedChange={(v) => setNegFloat(!!v)} /> Negative float only</label>
          <span className="ml-auto text-xs text-muted-foreground">{filtered.length} of {tasks.length}</span>
        </div>
        <div className="overflow-x-auto rounded-md border border-border/60">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Row</TableHead>
                <TableHead>Parent</TableHead>
                <TableHead>Lvl</TableHead>
                <TableHead>Task</TableHead>
                <TableHead>Phase</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>%</TableHead>
                <TableHead>Start</TableHead>
                <TableHead>End</TableHead>
                <TableHead>Baseline S</TableHead>
                <TableHead>Baseline F</TableHead>
                <TableHead>Var</TableHead>
                <TableHead>Float</TableHead>
                <TableHead>Crit</TableHead>
                <TableHead>Hold</TableHead>
                <TableHead>Owner</TableHead>
                <TableHead>Assigned</TableHead>
                <TableHead>Comment</TableHead>
                <TableHead>Health</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((t) => (
                <TableRow key={`${t.source_row}-${t.task_name}`}>
                  <TableCell className="font-mono text-xs">{t.source_row}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{t.parent_source_row ?? "—"}</TableCell>
                  <TableCell>{t.level}</TableCell>
                  <TableCell className="max-w-[280px] truncate" title={t.task_name}>{t.task_name}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{t.phase_milestone ?? "—"}</TableCell>
                  <TableCell>{t.status ?? "—"}</TableCell>
                  <TableCell>{t.percent_complete != null ? `${t.percent_complete}%` : "—"}</TableCell>
                  <TableCell className="text-xs">{t.start_date ?? "—"}</TableCell>
                  <TableCell className="text-xs">{t.end_date ?? "—"}</TableCell>
                  <TableCell className="text-xs">{t.baseline_start ?? "—"}</TableCell>
                  <TableCell className="text-xs">{t.baseline_finish ?? "—"}</TableCell>
                  <TableCell>{t.variance ?? "—"}</TableCell>
                  <TableCell className={t.total_float != null && t.total_float < 0 ? "text-rag-red font-semibold" : ""}>{t.total_float ?? "—"}</TableCell>
                  <TableCell>{t.critical ? "Yes" : ""}</TableCell>
                  <TableCell>{t.on_hold ? "Yes" : ""}</TableCell>
                  <TableCell className="text-sm">{t.owner ?? "—"}</TableCell>
                  <TableCell className="text-sm">{t.assigned_to ?? "—"}</TableCell>
                  <TableCell className="max-w-[240px] truncate text-sm text-muted-foreground" title={t.status_comment ?? ""}>{t.status_comment ?? "—"}</TableCell>
                  <TableCell><RagBadge status={t.source_schedule_health} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function CommentTable({ comments }: { comments: CommentRow[] }) {
  if (!comments.length) {
    return (
      <EmptyState
        icon={<MessageSquare className="h-8 w-8" />}
        title="No stakeholder comments were found in this workbook."
      />
    );
  }
  return (
    <Card>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Row</TableHead>
              <TableHead>Ref row</TableHead>
              <TableHead>Comment</TableHead>
              <TableHead>Author</TableHead>
              <TableHead>Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {comments.map((c) => (
              <TableRow key={c.source_row}>
                <TableCell className="font-mono text-xs">{c.source_row}</TableCell>
                <TableCell className="font-mono text-xs text-muted-foreground">{c.referenced_row ?? "—"}</TableCell>
                <TableCell className="max-w-[520px]">{c.comment_text}</TableCell>
                <TableCell className="text-sm">{c.author ?? "—"}</TableCell>
                <TableCell className="text-xs text-muted-foreground">{c.created_at_source ?? "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

// ── Trend Chart ─────────────────────────────────────────────────────────────

function TrendChart({ points, currentSnapshotId }: { points: TrendPoint[]; currentSnapshotId: number }) {
  if (points.length < 2) {
    return (
      <EmptyState
        icon={<TrendingUp className="h-8 w-8" />}
        title="Not enough data points"
        description="At least 2 snapshots of this project are required to show a historical trend."
      />
    );
  }

  // Map to recharts format
  const data = points.map((p) => ({
    date: p.run_date,
    score: p.rag_score,
    dq: p.data_quality_score,
    status: p.rag_status,
    snapshotId: p.snapshot_id,
    isCurrent: p.snapshot_id === currentSnapshotId,
  }));

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "red": return "#ef4444";
      case "amber": return "#f59e0b";
      case "green": return "#22c55e";
      default: return "#94a3b8";
    }
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (cx == null || cy == null) return null;
    return (
      <circle
        cx={cx}
        cy={cy}
        r={payload.isCurrent ? 6 : 4}
        stroke={payload.isCurrent ? "#000" : "#fff"}
        strokeWidth={2}
        fill={getStatusColor(payload.status)}
      />
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Historical RAG Score Trend</CardTitle>
        <CardDescription>Visualizing AI-scored project health over time.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[350px] w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 12 }} tickLine={false} axisLine={{ stroke: "#cbd5e1" }} />
              <YAxis yAxisId="left" domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 12 }} tickLine={false} axisLine={{ stroke: "#cbd5e1" }} />
              <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 12 }} tickLine={false} axisLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-lg border bg-background p-3 shadow-sm">
                        <div className="text-sm font-semibold mb-1">{data.date}</div>
                        <div className="flex items-center gap-2 text-sm">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getStatusColor(data.status) }} />
                          <span className="font-medium text-foreground">{data.status}</span>
                        </div>
                        <div className="text-sm mt-1">
                          <span className="text-muted-foreground">RAG Score:</span>{" "}
                          <span className="font-medium">{data.score?.toFixed(1)}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-muted-foreground">DQ Score:</span>{" "}
                          <span className="font-medium">{data.dq?.toFixed(1)}</span>
                        </div>
                        {data.isCurrent && (
                          <div className="text-xs text-primary font-medium mt-1">Current Snapshot</div>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "20px" }} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="score"
                name="RAG Score"
                stroke="#64748b"
                strokeWidth={2}
                dot={<CustomDot />}
                activeDot={{ r: 8 }}
                isAnimationActive={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="dq"
                name="Data Quality Score"
                stroke="#cbd5e1"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Gantt Chart ─────────────────────────────────────────────────────────────

function GanttChart({ tasks }: { tasks: TaskRow[] }) {
  if (!tasks.length) {
    return <EmptyState icon={<GitBranch className="h-8 w-8" />} title="No tasks found for Gantt chart" />;
  }

  // 1. Filter out tasks with no start/end dates
  const validTasks = tasks.filter((t) => t.start_date && t.end_date);
  if (validTasks.length === 0) {
    return <EmptyState icon={<GitBranch className="h-8 w-8" />} title="Tasks lack valid dates" description="Start or End dates are missing." />;
  }

  // 2. Determine timeline bounds
  const minTime = Math.min(...validTasks.map((t) => new Date(t.start_date!).getTime()));
  const maxTime = Math.max(...validTasks.map((t) => new Date(t.end_date!).getTime()));
  
  if (isNaN(minTime) || isNaN(maxTime) || minTime >= maxTime) {
    return <EmptyState icon={<GitBranch className="h-8 w-8" />} title="Invalid date ranges" description="Dates could not be parsed correctly." />;
  }

  // 3. Setup dimensions
  const DAY_MS = 1000 * 60 * 60 * 24;
  const totalDays = Math.ceil((maxTime - minTime) / DAY_MS);
  
  const ROW_HEIGHT = 28;
  const HEADER_HEIGHT = 40;
  const LEFT_LABEL_WIDTH = 300;
  
  // Use a minimum pixel width per day to ensure readability, max of what fits
  const pixelsPerDay = Math.max(3, Math.min(10, 800 / totalDays));
  const chartWidth = totalDays * pixelsPerDay;
  const svgHeight = HEADER_HEIGHT + validTasks.length * ROW_HEIGHT + 20;

  const todayTime = new Date().getTime();
  const todayX = ((todayTime - minTime) / DAY_MS) * pixelsPerDay;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "red": return "#ef4444";
      case "amber": case "yellow": return "#f59e0b";
      case "green": return "#22c55e";
      default: return "#94a3b8"; // Slate for grey/unspecified
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Schedule Gantt View</CardTitle>
        <CardDescription>Grey dashed bars indicate baseline finish. Red outline indicates critical path.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto border rounded-md">
          <svg width={LEFT_LABEL_WIDTH + chartWidth + 40} height={svgHeight} className="text-sm font-sans bg-white">
            
            {/* Header Background */}
            <rect x={0} y={0} width="100%" height={HEADER_HEIGHT} fill="#f8fafc" borderBottom="1px solid #e2e8f0" />
            <line x1={0} y1={HEADER_HEIGHT} x2="100%" y2={HEADER_HEIGHT} stroke="#e2e8f0" />

            {/* Labels header */}
            <text x={10} y={25} fill="#64748b" fontWeight={600} fontSize={12}>Task Name</text>
            <text x={LEFT_LABEL_WIDTH - 60} y={25} fill="#64748b" fontWeight={600} fontSize={12}>Status</text>
            
            {/* Timeline ticks (approx monthly if long, weekly if short) */}
            {Array.from({ length: Math.ceil(totalDays / 30) }).map((_, i) => {
              const tickDays = i * 30;
              const tickX = LEFT_LABEL_WIDTH + (tickDays * pixelsPerDay);
              const tickDate = new Date(minTime + tickDays * DAY_MS);
              return (
                <g key={i}>
                  <line x1={tickX} y1={HEADER_HEIGHT - 5} x2={tickX} y2={svgHeight} stroke="#e2e8f0" strokeDasharray="4 4" />
                  <text x={tickX + 4} y={25} fill="#94a3b8" fontSize={11}>{tickDate.toLocaleDateString(undefined, { month: 'short', year: '2-digit' })}</text>
                </g>
              );
            })}

            {/* Today line */}
            {todayX >= 0 && todayX <= chartWidth && (
              <g>
                <line x1={LEFT_LABEL_WIDTH + todayX} y1={0} x2={LEFT_LABEL_WIDTH + todayX} y2={svgHeight} stroke="#ef4444" strokeDasharray="2 2" strokeWidth={1.5} />
                <text x={LEFT_LABEL_WIDTH + todayX + 4} y={15} fill="#ef4444" fontSize={10} fontWeight={600}>TODAY</text>
              </g>
            )}

            {/* Tasks */}
            {validTasks.map((t, idx) => {
              const y = HEADER_HEIGHT + idx * ROW_HEIGHT;
              const startT = new Date(t.start_date!).getTime();
              const endT = new Date(t.end_date!).getTime();
              
              const xStart = LEFT_LABEL_WIDTH + ((startT - minTime) / DAY_MS) * pixelsPerDay;
              const xEnd = LEFT_LABEL_WIDTH + ((endT - minTime) / DAY_MS) * pixelsPerDay;
              const w = Math.max(xEnd - xStart, 4); // min width 4px

              // Indentation
              const indent = ((t.level || 1) - 1) * 12;
              
              // Colors
              const color = getStatusColor(t.source_schedule_health);
              const isMilestone = t.percent_complete === 100 || (t.phase_milestone && t.phase_milestone.toLowerCase().includes("milestone"));

              return (
                <g key={t.source_row} className="hover:opacity-80 transition-opacity">
                  {/* Row background hover area */}
                  <rect x={0} y={y} width="100%" height={ROW_HEIGHT} fill={idx % 2 === 0 ? "#ffffff" : "#f8fafc"} />
                  <line x1={0} y1={y + ROW_HEIGHT} x2="100%" y2={y + ROW_HEIGHT} stroke="#f1f5f9" />

                  {/* Task Name */}
                  <text x={10 + indent} y={y + 18} fill="#334155" fontSize={12} className="truncate">
                    {t.task_name.length > 40 ? t.task_name.substring(0, 40) + "..." : t.task_name}
                  </text>
                  
                  {/* Status Badge */}
                  <circle cx={LEFT_LABEL_WIDTH - 45} cy={y + 14} r={4} fill={color} />

                  {/* Baseline indicator (if exists) */}
                  {t.baseline_finish && (
                    <rect 
                      x={LEFT_LABEL_WIDTH + ((new Date(t.baseline_start || t.start_date!).getTime() - minTime) / DAY_MS) * pixelsPerDay}
                      y={y + 12}
                      width={Math.max(((new Date(t.baseline_finish).getTime() - new Date(t.baseline_start || t.start_date!).getTime()) / DAY_MS) * pixelsPerDay, 2)}
                      height={4}
                      fill="#cbd5e1"
                    />
                  )}

                  {/* Main Task Bar */}
                  {isMilestone ? (
                    <polygon 
                      points={`${xEnd},${y + 8} ${xEnd + 6},${y + 14} ${xEnd},${y + 20} ${xEnd - 6},${y + 14}`} 
                      fill={color} 
                      stroke={t.critical ? "#ef4444" : "none"}
                      strokeWidth={t.critical ? 1.5 : 0}
                    />
                  ) : (
                    <rect 
                      x={xStart} 
                      y={y + 6} 
                      width={w} 
                      height={16} 
                      rx={3} 
                      fill={color} 
                      fillOpacity={0.8}
                      stroke={t.critical ? "#ef4444" : "none"}
                      strokeWidth={t.critical ? 2 : 0}
                    />
                  )}
                  
                  {/* Percent Complete overlay */}
                  {!isMilestone && t.percent_complete != null && t.percent_complete > 0 && (
                    <rect 
                      x={xStart} 
                      y={y + 12} 
                      width={w * (t.percent_complete / 100)} 
                      height={4} 
                      fill="#000" 
                      fillOpacity={0.2}
                      rx={1}
                    />
                  )}
                </g>
              );
            })}
          </svg>
        </div>
      </CardContent>
    </Card>
  );
}
