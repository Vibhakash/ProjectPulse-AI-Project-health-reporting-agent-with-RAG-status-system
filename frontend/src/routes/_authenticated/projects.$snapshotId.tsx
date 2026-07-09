import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type CommentRow, type Signal, type TaskRow } from "@/lib/api";
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
import { AlertTriangle, ArrowLeft, Bot, Brain, Loader2, MessageSquare, TrendingUp, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
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
                  {s.agent_mode && s.agent_mode !== "offline" ? (
                    <Badge className="gap-1 bg-primary/10 text-primary border-primary/30">
                      <Bot className="h-3 w-3" />{s.agent_mode.replace("llm:", "")}
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="gap-1">
                      <Brain className="h-3 w-3" />Rule engine
                    </Badge>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/30 ml-2"
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
              <TabsTrigger value="comments">Comments</TabsTrigger>
              <TabsTrigger value="attributes">Preserved attributes</TabsTrigger>
            </TabsList>

            <TabsContent value="reasoning" className="mt-4 space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <ListCard title="Reasons" items={s.reasons} empty="No reasoning provided." />
                <ListCard title="Top risks" items={s.top_risks} empty="No top risks flagged." icon={<AlertTriangle className="h-4 w-4 text-rag-red" />} />
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
            {isLlm ? `OpenAI · ${agentMode?.replace("llm:", "")}` : "Deterministic offline mode"}
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
