import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { EmptyState, ErrorState } from "@/components/empty-state";
import { Loader2, MessageSquare, Search } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const Route = createFileRoute("/_authenticated/ask")({
  component: AskPage,
});

const EXAMPLES = [
  "Which projects have external dependency blockers?",
  "red projects",
  "Show critical tasks with negative float",
];

function AskPage() {
  const [q, setQ] = useState("");
  const m = useMutation({ mutationFn: (question: string) => api.ask(question) });

  function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const trimmed = q.trim();
    if (!trimmed) return;
    m.mutate(trimmed);
  }

  const rows = m.data?.rows ?? [];
  const columns = rows.length ? Object.keys(rows[0]) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Ask your project data</h1>
        <p className="text-sm text-muted-foreground">
          A simple natural-language query over the backend SQLite store. Results come directly from the backend.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2"><MessageSquare className="h-4 w-4" /> Query</CardTitle>
          <CardDescription>Try one of the examples or ask your own.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <form onSubmit={submit} className="flex gap-2">
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="e.g. Which projects have external dependency blockers?"
            />
            <Button type="submit" disabled={m.isPending || !q.trim()}>
              {m.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            </Button>
          </form>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => { setQ(ex); m.mutate(ex); }}
                className="rounded-full border border-border/70 bg-muted/40 px-3 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-accent"
              >
                {ex}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {m.isError ? (
        <ErrorState message={(m.error as Error).message} onRetry={() => m.mutate(q)} />
      ) : m.isSuccess && rows.length === 0 ? (
        <EmptyState title="No rows matched your question." description="Try a different phrasing or check the examples above." />
      ) : rows.length ? (
        <Card>
          <CardHeader><CardTitle className="text-sm">Results ({rows.length})</CardTitle></CardHeader>
          <CardContent className="p-0 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.map((c) => <TableHead key={c} className="font-mono text-xs">{c}</TableHead>)}
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((r, i) => (
                  <TableRow key={i}>
                    {columns.map((c) => (
                      <TableCell key={c} className="text-sm">{formatCell(r[c])}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function formatCell(v: unknown): string {
  if (v == null) return "—";
  if (typeof v === "boolean") return v ? "Yes" : "No";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}