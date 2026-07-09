import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api, fileDownloadUrl } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { FileDown, Loader2, Presentation, RefreshCw } from "lucide-react";
import { RagBadge } from "@/components/rag-badge";
import { toast } from "sonner";
import { useState } from "react";

export const Route = createFileRoute("/_authenticated/reports")({
  component: ReportsPage,
});

function ReportsPage() {
  const q = useQuery({ queryKey: ["portfolio"], queryFn: api.portfolio, retry: 1 });
  const [deckPath, setDeckPath] = useState<string | null>(null);
  const monthly = useMutation({
    mutationFn: api.monthlySynthesis,
    onSuccess: (r) => {
      setDeckPath(r.deck_path);
      toast.success("Monthly deck generated");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const projects = q.data?.projects ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reports &amp; downloads</h1>
          <p className="text-sm text-muted-foreground">Weekly Markdown/JSON per project, plus the monthly executive deck.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => q.refetch()}>
          <RefreshCw className={`h-4 w-4 mr-1.5 ${q.isFetching ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2"><Presentation className="h-4 w-4" /> Monthly executive deck</CardTitle>
          <CardDescription>Generates a PowerPoint executive summary from the latest snapshots.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={() => monthly.mutate()} disabled={monthly.isPending}>
              {monthly.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Generate monthly PPTX
            </Button>
            {deckPath ? (
              <Button variant="outline" asChild>
                <a href={fileDownloadUrl(deckPath)} target="_blank" rel="noreferrer">
                  <FileDown className="h-4 w-4 mr-1.5" /> Download deck
                </a>
              </Button>
            ) : null}
          </div>
          {monthly.isError ? <ErrorState message={(monthly.error as Error).message} /> : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Weekly reports</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading ? (
            <div className="py-6 text-sm text-muted-foreground flex items-center gap-2 justify-center">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading…
            </div>
          ) : q.isError ? (
            <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} />
          ) : projects.length === 0 ? (
            <EmptyState title="No weekly reports available yet." description="Upload plans and run analysis to generate reports." />
          ) : (
            <ul className="divide-y rounded-md border border-border/60">
              {projects.map((p) => (
                <li key={p.snapshot_id} className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
                  <div className="min-w-0">
                    <div className="truncate font-medium">{p.name}</div>
                    <div className="text-xs text-muted-foreground">Run {p.run_date}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <RagBadge status={p.rag_status} />
                    {p.weekly_markdown_path ? (
                      <Button variant="outline" size="sm" asChild>
                        <a href={fileDownloadUrl(p.weekly_markdown_path)} target="_blank" rel="noreferrer">
                          <FileDown className="h-3.5 w-3.5 mr-1" /> Markdown
                        </a>
                      </Button>
                    ) : null}
                    {p.weekly_json_path ? (
                      <Button variant="outline" size="sm" asChild>
                        <a href={fileDownloadUrl(p.weekly_json_path)} target="_blank" rel="noreferrer">
                          <FileDown className="h-3.5 w-3.5 mr-1" /> JSON
                        </a>
                      </Button>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}