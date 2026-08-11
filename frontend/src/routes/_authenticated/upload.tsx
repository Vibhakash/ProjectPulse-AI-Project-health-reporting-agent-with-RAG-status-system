import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api, ApiError, type AnalyzeResponse } from "@/lib/api";
import { RagBadge } from "@/components/rag-badge";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { FileSpreadsheet, FileArchive, Loader2, Upload as UploadIcon, X, Download, Info, CheckCircle2 } from "lucide-react";
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
    const list = Array.from(e.target.files ?? []).filter((f) => {
      const n = f.name.toLowerCase();
      return n.endsWith(".xlsx") || n.endsWith(".zip");
    });
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
        <h1 className="text-2xl font-bold tracking-tight">Upload & analyze</h1>
        <p className="text-sm text-muted-foreground">
          Upload one or more .xlsx project plan workbooks. The backend runs the RAG engine and returns snapshots.
        </p>
      </div>

      {/* Template download banner */}
      <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/15">
            <FileSpreadsheet className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-1 flex items-center gap-2">
              <Info className="h-4 w-4" /> Use the Official Project Plan Template
            </div>
            <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
              Download our pre-formatted Excel template to ensure all required columns are present before uploading.
              The template includes required column markers, dropdown validations, sample data, and a full column reference guide.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground mb-3">
              {[
                "Task Name, Status, % Complete",
                "Schedule Health (Red/Amber/Green)",
                "Start/End/Baseline Finish Dates",
                "Total Float & Critical Path flag",
              ].map((req) => (
                <span key={req} className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                  {req}
                </span>
              ))}
            </div>
            <a
              href="/api/template"
              download="ProjectPulseAI_Project_Plan_Template.xlsx"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
            >
              <Download className="h-3.5 w-3.5" />
              Download Template (.xlsx)
            </a>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><UploadIcon className="h-4 w-4" /> New analysis run</CardTitle>
          <CardDescription>.xlsx files or a .zip archive containing multiple .xlsx files are accepted.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-[1fr_200px]">
            <div className="space-y-1.5">
              <Label htmlFor="files">Project plan files</Label>
              <Input id="files" type="file" accept=".xlsx,.zip" multiple onChange={onSelect} />
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
                    {f.name.toLowerCase().endsWith(".zip")
                      ? <FileArchive className="h-4 w-4 text-amber-500 shrink-0" />
                      : <FileSpreadsheet className="h-4 w-4 text-primary shrink-0" />}
                    <span className="truncate">{f.name}</span>
                    <span className="text-xs text-muted-foreground">{(f.size / 1024).toFixed(0)} KB</span>
                    {f.name.toLowerCase().endsWith(".zip") && (
                      <span className="text-[10px] font-semibold bg-amber-500/15 text-amber-600 px-1.5 py-0.5 rounded-full">ZIP</span>
                    )}
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