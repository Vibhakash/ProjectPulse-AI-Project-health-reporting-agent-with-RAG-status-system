import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { RagBadge } from "@/components/rag-badge";
import { Brain, Info, ShieldCheck, ScrollText } from "lucide-react";

export const Route = createFileRoute("/_authenticated/methodology")({
  component: MethodologyPage,
});

function MethodologyPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2"><ScrollText className="h-5 w-5" /> How Project Works</h1>
        <p className="text-sm text-muted-foreground">
          How ProjectPulse AI derives project health. The backend rule engine is the single source of truth.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2"><Brain className="h-4 w-4" /> Deterministic RAG scoring</CardTitle>
          <CardDescription>Weighted signals — not LLM guesswork.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>
            Each project snapshot is scored by a deterministic rule engine (<code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">src/project_health/rag_engine.py</code>)
            using weights defined in <code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">config/rag_weights.json</code>.
          </p>
          <p>
            Every signal contributes a weighted score with evidence recorded in the SQLite <code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">rag_signals</code> table.
            The frontend never calculates RAG values; it only displays what the backend returns.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">RAG legend</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex items-center gap-3"><RagBadge status="Red" /> High-risk — needs leadership attention now.</div>
          <div className="flex items-center gap-3"><RagBadge status="Amber" /> Watch-list — trending negative or missing evidence.</div>
          <div className="flex items-center gap-3"><RagBadge status="Green" /> Healthy — on plan with acceptable data quality.</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2"><ShieldCheck className="h-4 w-4" /> What we never do</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-1.5 text-sm">
            <li className="flex gap-2"><span className="text-muted-foreground">•</span> Invent metrics, comments, or budgets not present in your workbook.</li>
            <li className="flex gap-2"><span className="text-muted-foreground">•</span> Show trend lines without at least two snapshots.</li>
            <li className="flex gap-2"><span className="text-muted-foreground">•</span> Recalculate signal weights in the browser.</li>
            <li className="flex gap-2"><span className="text-muted-foreground">•</span> Modify your source project plan.</li>
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2"><Info className="h-4 w-4" /> Source schedule health vs agent RAG</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2">
          <p><b>Source schedule health</b> is whatever the uploaded workbook stated (from PM input or scheduling tool).</p>
          <p><b>Agent RAG</b> is the deterministic engine's independent conclusion. Both are shown so leadership can see disagreement.</p>
        </CardContent>
      </Card>
    </div>
  );
}