import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api, ApiError, type AnalyzeResponse } from "@/lib/api";
import { RagBadge } from "@/components/rag-badge";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { FileSpreadsheet, Loader2, Upload as UploadIcon, X } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/upload")({
  component: UploadPage,
});

function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [runDate, setRunDate] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function onSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const list = Array.from(e.target.files ?? []).filter((f) => f.name.toLowerCase().endsWith(".xlsx"));
    setFiles((prev) => {
      const seen = new Set(prev.map((p) => p.name + p.size));
      const merged = [...prev];
      list.forEach((f) => {
        if (!seen.has(f.name + f.size)) merged.push(f);
      });
      return merged;
    });
    e.target.value = "";
  }
  function remove(idx: number) {
    setFiles((f) => f.filter((_, i) => i !== idx));
  }

  async function submit() {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.analyze(files, runDate || undefined);
      setResult(res);
      toast.success(`Analyzed ${res.snapshots.length} project${res.snapshots.length === 1 ? "" : "s"}`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : err instanceof Error ? err.message : "Analysis failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Upload &amp; analyze</h1>
        <p className="text-sm text-muted-foreground">
          Upload one or more .xlsx project plan workbooks. The backend runs the RAG engine and returns snapshots.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><UploadIcon className="h-4 w-4" /> New analysis run</CardTitle>
          <CardDescription>Only .xlsx files are accepted.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-[1fr_200px]">
            <div className="space-y-1.5">
              <Label htmlFor="files">Project plan files</Label>
              <Input id="files" type="file" accept=".xlsx" multiple onChange={onSelect} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="run-date">Run date (optional)</Label>
              <Input id="run-date" type="date" value={runDate} onChange={(e) => setRunDate(e.target.value)} />
            </div>
          </div>

          {files.length > 0 ? (
            <ul className="divide-y rounded-md border border-border/60">
              {files.map((f, i) => (
                <li key={f.name + i} className="flex items-center justify-between px-3 py-2 text-sm">
                  <span className="flex items-center gap-2 truncate">
                    <FileSpreadsheet className="h-4 w-4 text-primary shrink-0" />
                    <span className="truncate">{f.name}</span>
                    <span className="text-xs text-muted-foreground">{(f.size / 1024).toFixed(0)} KB</span>
                  </span>
                  <Button variant="ghost" size="icon" aria-label="Remove" onClick={() => remove(i)}>
                    <X className="h-4 w-4" />
                  </Button>
                </li>
              ))}
            </ul>
          ) : null}

          <div className="flex items-center gap-2">
            <Button onClick={submit} disabled={!files.length || loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Run analysis
            </Button>
            {loading ? <span className="text-xs text-muted-foreground">Running backend analysis…</span> : null}
          </div>

          {error ? <ErrorState message={error} onRetry={submit} /> : null}
        </CardContent>
      </Card>

      {result ? (
        <Card>
          <CardHeader>
            <CardTitle>Analysis complete</CardTitle>
            <CardDescription>Run date: {result.run_date}</CardDescription>
          </CardHeader>
          <CardContent>
            {result.snapshots.length === 0 ? (
              <EmptyState title="No snapshots returned" description="The backend accepted the upload but returned no snapshots." />
            ) : (
              <ul className="divide-y rounded-md border border-border/60">
                {result.snapshots.map((s) => (
                  <li key={s.snapshot_id} className="flex items-center justify-between gap-3 px-3 py-2">
                    <div className="min-w-0">
                      <div className="truncate font-medium">{s.project_name}</div>
                      <div className="text-xs text-muted-foreground">
                        Score {s.rag_score.toFixed(1)} · Confidence {s.confidence} · DQ {s.data_quality_score.toFixed(1)}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <RagBadge status={s.rag_status} />
                      <Button size="sm" variant="outline" onClick={() => router.navigate({ to: "/projects/$snapshotId", params: { snapshotId: String(s.snapshot_id) } })}>
                        Open
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}