import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type PortfolioProject } from "@/lib/api";
import { RagBadge, RagDot } from "@/components/rag-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { BarChart3, ExternalLink, FileDown, Loader2, RefreshCw, Upload, Trash2 } from "lucide-react";
import { fileDownloadUrl } from "@/lib/api";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { useMemo } from "react";

export const Route = createFileRoute("/_authenticated/portfolio")({
  component: PortfolioPage,
});

function ragCounts(projects: PortfolioProject[]) {
  const c = { Red: 0, Amber: 0, Green: 0, Other: 0 };
  for (const p of projects) {
    const k = (p.rag_status ?? "").toString();
    if (k === "Red" || k === "Amber" || k === "Green") c[k]++;
    else c.Other++;
  }
  return c;
}

const RAG_COLORS: Record<string, string> = {
  Red: "var(--rag-red)",
  Amber: "var(--rag-amber)",
  Green: "var(--rag-green)",
  Other: "var(--muted-foreground)",
};

function PortfolioPage() {
  const q = useQuery({ queryKey: ["portfolio"], queryFn: api.portfolio, retry: 1 });

  const projects = q.data?.projects ?? [];
  const counts = useMemo(() => ragCounts(projects), [projects]);
  const pie = Object.entries(counts)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }));
  const dq = projects.map((p) => ({ name: p.name.slice(0, 18), dq: p.data_quality_score }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Portfolio health</h1>
          <p className="text-sm text-muted-foreground">Latest backend-generated snapshot per project.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => q.refetch()}>
            <RefreshCw className={`h-4 w-4 mr-1.5 ${q.isFetching ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button size="sm" asChild>
            <Link to="/upload"><Upload className="h-4 w-4 mr-1.5" /> Upload plans</Link>
          </Button>
        </div>
      </div>

      {q.isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground py-10 justify-center">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading portfolio…
        </div>
      ) : q.isError ? (
        <ErrorState
          title="Couldn't load portfolio"
          message={(q.error as Error).message}
          onRetry={() => q.refetch()}
        />
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<BarChart3 className="h-8 w-8" />}
          title="No project snapshots available yet"
          description="Upload project plans and run analysis to see portfolio health here."
          action={
            <Button asChild>
              <Link to="/upload"><Upload className="h-4 w-4 mr-1.5" /> Upload plans</Link>
            </Button>
          }
        />
      ) : (
        <>
          {/* Summary counts */}
          <div className="grid gap-4 sm:grid-cols-4">
            {(["Red", "Amber", "Green"] as const).map((k) => (
              <Card key={k}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-2">
                    <RagDot status={k} /> {k}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{counts[k]}</div>
                  <div className="text-xs text-muted-foreground">
                    {counts[k] === 1 ? "project" : "projects"}
                  </div>
                </CardContent>
              </Card>
            ))}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Total</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{projects.length}</div>
                <div className="text-xs text-muted-foreground">tracked projects</div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="text-sm">RAG distribution</CardTitle></CardHeader>
              <CardContent style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pie} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={2}>
                      {pie.map((entry) => (
                        <Cell key={entry.name} fill={RAG_COLORS[entry.name] ?? "var(--muted-foreground)"} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        color: "var(--popover-foreground)",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">Data quality by project</CardTitle></CardHeader>
              <CardContent style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dq}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} />
                    <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        color: "var(--popover-foreground)",
                      }}
                    />
                    <Bar dataKey="dq" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Table */}
          <Card>
            <CardHeader><CardTitle className="text-sm">Projects</CardTitle></CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Project</TableHead>
                      <TableHead>RAG</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>DQ</TableHead>
                      <TableHead>Stage</TableHead>
                      <TableHead>Schedule health</TableHead>
                      <TableHead>Run date</TableHead>
                      <TableHead className="text-right">Report</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {projects.map((p) => (
                      <TableRow key={p.snapshot_id}>
                        <TableCell className="font-medium">
                          <Link
                            to="/projects/$snapshotId"
                            params={{ snapshotId: String(p.snapshot_id) }}
                            className="hover:underline flex items-center gap-1"
                          >
                            {p.name} <ExternalLink className="h-3 w-3 opacity-60" />
                          </Link>
                          {p.project_manager ? (
                            <div className="text-xs text-muted-foreground">PM: {p.project_manager}</div>
                          ) : null}
                        </TableCell>
                        <TableCell><RagBadge status={p.rag_status} /></TableCell>
                        <TableCell>{p.rag_score?.toFixed?.(1) ?? "—"}</TableCell>
                        <TableCell>{p.confidence ?? "—"}</TableCell>
                        <TableCell>{p.data_quality_score?.toFixed?.(1) ?? "—"}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">{p.project_stage ?? "—"}</TableCell>
                        <TableCell><RagBadge status={p.source_schedule_health} /></TableCell>
                        <TableCell className="text-sm text-muted-foreground">{p.run_date}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end items-center gap-1">
                            {p.weekly_markdown_path ? (
                              <Button asChild variant="ghost" size="sm">
                                <a href={fileDownloadUrl(p.weekly_markdown_path)} target="_blank" rel="noreferrer">
                                  <FileDown className="h-3.5 w-3.5 mr-1" /> MD
                                </a>
                              </Button>
                            ) : null}
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:bg-destructive/10 hover:text-destructive h-8 w-8 p-0"
                              title="Delete snapshot"
                              onClick={async () => {
                                if (confirm(`Are you sure you want to delete the snapshot for project "${p.name}"?`)) {
                                  try {
                                    await api.deleteSnapshot(p.snapshot_id);
                                    q.refetch();
                                  } catch (err) {
                                    alert(err instanceof Error ? err.message : "Failed to delete snapshot");
                                  }
                                }
                              }}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}