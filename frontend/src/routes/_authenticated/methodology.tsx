import { createFileRoute } from "@tanstack/react-router";
import { RagBadge } from "@/components/rag-badge";
import {
  Brain,
  ShieldCheck,
  ArrowRight,
  Upload,
  BarChart3,
  FileDown,
  Layers,
  Cpu,
  AlertTriangle,
  CheckCircle2,
  Info,
  Zap,
  Database,
  Lock,
} from "lucide-react";

export const Route = createFileRoute("/_authenticated/methodology")({
  component: MethodologyPage,
});

function MethodologyPage() {
  const steps = [
    {
      icon: <Upload className="h-5 w-5" />,
      step: "01",
      title: "Upload Your Project Plan",
      desc: "Drag and drop any .xlsx workbook exported from MS Project, Primavera, or any PM tool. The system reads all sheets and preserves every column.",
      color: "from-violet-500/20 to-violet-500/5 border-violet-500/30",
      iconBg: "bg-violet-500/15 text-violet-500",
    },
    {
      icon: <Cpu className="h-5 w-5" />,
      step: "02",
      title: "Deterministic Rule Engine Runs",
      desc: "Six weighted signal layers — schedule slippage, progress gap, milestone health, blockers, sentiment, and budget — are computed without any guesswork.",
      color: "from-blue-500/20 to-blue-500/5 border-blue-500/30",
      iconBg: "bg-blue-500/15 text-blue-500",
    },
    {
      icon: <Brain className="h-5 w-5" />,
      step: "03",
      title: "AI Agent Generates Narratives",
      desc: "Once scores are computed, the LLM agent reads the verified metrics and writes human-readable executive summaries, risk themes, and recommendations.",
      color: "from-indigo-500/20 to-indigo-500/5 border-indigo-500/30",
      iconBg: "bg-indigo-500/15 text-indigo-500",
    },
    {
      icon: <Database className="h-5 w-5" />,
      step: "04",
      title: "Snapshot Saved to Database",
      desc: "All raw task data, computed signals, RAG status, and AI narratives are saved as an immutable snapshot in the local SQLite database for full auditability.",
      color: "from-cyan-500/20 to-cyan-500/5 border-cyan-500/30",
      iconBg: "bg-cyan-500/15 text-cyan-500",
    },
    {
      icon: <BarChart3 className="h-5 w-5" />,
      step: "05",
      title: "Dashboard Comes Alive",
      desc: "View the health score, signal breakdown, task evidence, and AI insights — all in one place. Switch between projects using the portfolio switcher.",
      color: "from-emerald-500/20 to-emerald-500/5 border-emerald-500/30",
      iconBg: "bg-emerald-500/15 text-emerald-500",
    },
    {
      icon: <FileDown className="h-5 w-5" />,
      step: "06",
      title: "Export Monthly PPTX Report",
      desc: "Generate a polished, executive-ready PowerPoint presentation covering the full portfolio — automatically compiled from every snapshot in the database.",
      color: "from-amber-500/20 to-amber-500/5 border-amber-500/30",
      iconBg: "bg-amber-500/15 text-amber-500",
    },
  ];

  const signals = [
    { name: "Schedule Slippage", weight: "30%", color: "bg-red-500", desc: "Red/Amber/Yellow flags, float erosion, late active tasks" },
    { name: "Progress Gap", weight: "20%", color: "bg-orange-500", desc: "Actual % complete vs expected linear progress" },
    { name: "Milestone Health", weight: "20%", color: "bg-yellow-500", desc: "Delayed or high-risk key milestones ratio" },
    { name: "Blockers & Critical Path", weight: "15%", color: "bg-purple-500", desc: "Critical tasks, negative float, dependency blockers" },
    { name: "Stakeholder Sentiment", weight: "10%", color: "bg-blue-500", desc: "Tone & urgency analysis of PM comments" },
    { name: "Budget Burn", weight: "5%", color: "bg-green-500", desc: "Cost variance and burn rate (skipped if absent)" },
  ];

  const guarantees = [
    { icon: <Lock className="h-4 w-4" />, text: "Never invents metrics, comments, or budgets not present in your workbook" },
    { icon: <ShieldCheck className="h-4 w-4" />, text: "Never recalculates signal weights in the browser — all computation stays on the server" },
    { icon: <CheckCircle2 className="h-4 w-4" />, text: "Never modifies your source project plan — read-only ingestion only" },
    { icon: <AlertTriangle className="h-4 w-4" />, text: "Never shows trend lines without at least two snapshots for comparison" },
  ];

  return (
    <div className="space-y-10 max-w-5xl pb-10">

      {/* Hero header */}
      <div className="relative rounded-2xl overflow-hidden border border-border/60 bg-gradient-to-br from-primary/10 via-background to-background p-8">
        <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-primary/5 blur-3xl pointer-events-none" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary mb-4">
            <Zap className="h-3 w-3" /> Platform Overview
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            How ProjectPulse AI Works
          </h1>
          <p className="text-muted-foreground max-w-2xl leading-relaxed">
            ProjectPulse AI is a fully automated project health reporting platform. It ingests your Excel project plans,
            runs a deterministic scoring engine, and produces auditable RAG status reports — all without manual input or guesswork.
          </p>
        </div>
      </div>

      {/* How it works steps */}
      <section>
        <h2 className="text-lg font-semibold mb-1 flex items-center gap-2">
          <Layers className="h-5 w-5 text-primary" /> End-to-End Pipeline
        </h2>
        <p className="text-sm text-muted-foreground mb-5">Six stages from raw Excel data to executive presentation — fully automated.</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {steps.map((s) => (
            <div
              key={s.step}
              className={`relative rounded-xl border bg-gradient-to-br p-5 transition-all hover:shadow-md hover:-translate-y-0.5 ${s.color}`}
            >
              <div className="flex items-start justify-between mb-3">
                <span className={`flex h-9 w-9 items-center justify-center rounded-lg ${s.iconBg}`}>
                  {s.icon}
                </span>
                <span className="text-3xl font-black text-foreground/10 select-none">{s.step}</span>
              </div>
              <h3 className="font-semibold text-sm mb-1.5">{s.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Signal weights visual */}
      <section>
        <h2 className="text-lg font-semibold mb-1 flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" /> The 6 Scoring Signals
        </h2>
        <p className="text-sm text-muted-foreground mb-5">
          Each signal contributes a weighted score (0–100). The final score maps to a RAG status deterministically.
        </p>
        <div className="rounded-xl border border-border/60 overflow-hidden divide-y divide-border/60">
          {signals.map((sig) => (
            <div key={sig.name} className="flex items-center gap-4 px-5 py-3.5 hover:bg-muted/30 transition-colors">
              <div className="w-32 shrink-0">
                <div className="text-sm font-medium leading-tight">{sig.name}</div>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-1.5 rounded-full bg-muted flex-1 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${sig.color}`}
                      style={{ width: sig.weight }}
                    />
                  </div>
                  <span className="text-xs font-bold text-foreground w-8 text-right shrink-0">{sig.weight}</span>
                </div>
                <div className="text-xs text-muted-foreground">{sig.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* RAG Legend */}
      <section>
        <h2 className="text-lg font-semibold mb-1 flex items-center gap-2">
          <Info className="h-5 w-5 text-primary" /> RAG Status Legend
        </h2>
        <p className="text-sm text-muted-foreground mb-4">The final weighted score maps to one of three statuses. Critical override rules can force a project to Red.</p>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { status: "Green" as const, range: "Score 0 – 34", headline: "On Track", detail: "Project is executing smoothly. No critical overrides triggered. Data quality is sufficient." },
            { status: "Amber" as const, range: "Score 35 – 69", headline: "Under Watch", detail: "Minor delays or missing evidence detected. Leadership should monitor but no immediate escalation needed." },
            { status: "Red" as const, range: "Score 70 – 100", headline: "Critical — Escalate", detail: "Significant delays, blocked milestones, or override rules triggered. Leadership attention required now." },
          ].map((item) => (
            <div key={item.status} className="rounded-xl border border-border/60 p-4 space-y-2 hover:shadow-sm transition-shadow">
              <div className="flex items-center justify-between">
                <RagBadge status={item.status} />
                <span className="text-xs text-muted-foreground font-mono">{item.range}</span>
              </div>
              <div className="font-semibold text-sm">{item.headline}</div>
              <p className="text-xs text-muted-foreground leading-relaxed">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Override rules */}
      <section>
        <h2 className="text-lg font-semibold mb-1 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-destructive" /> Critical Override Rules
        </h2>
        <p className="text-sm text-muted-foreground mb-4">These rules immediately force a project to <strong>Red</strong> regardless of the weighted score.</p>
        <div className="grid gap-2 sm:grid-cols-2">
          {[
            { rule: "Severe Critical Path Delay", detail: "An uncompleted critical task delayed by more than 15 working days." },
            { rule: "Milestone Failure", detail: "A key milestone missed its baseline finish by more than 30 days and remains incomplete." },
            { rule: "Multiple Active Blockers", detail: "More than 3 tasks flagged as blocked by external dependencies." },
            { rule: "Widespread Red Schedule", detail: "Over 40% of active tasks flagged as Red or Yellow schedule health." },
          ].map((item) => (
            <div key={item.rule} className="flex gap-3 rounded-lg border border-destructive/20 bg-destructive/5 px-4 py-3">
              <ArrowRight className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-semibold text-destructive">{item.rule}</div>
                <div className="text-xs text-muted-foreground mt-0.5">{item.detail}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Integrity guarantees */}
      <section>
        <h2 className="text-lg font-semibold mb-1 flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-emerald-500" /> Platform Integrity Guarantees
        </h2>
        <p className="text-sm text-muted-foreground mb-4">What this platform promises it will never do — by design.</p>
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 divide-y divide-emerald-500/10">
          {guarantees.map((g, i) => (
            <div key={i} className="flex items-center gap-3 px-5 py-3.5">
              <span className="text-emerald-500 shrink-0">{g.icon}</span>
              <span className="text-sm">{g.text}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Source vs Agent */}
      <section className="rounded-xl border border-border/60 bg-muted/20 p-6">
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <Info className="h-4 w-4 text-primary" /> Source Schedule Health vs. Agent RAG — What's the Difference?
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 text-sm">
          <div className="space-y-1.5">
            <div className="font-semibold flex items-center gap-2"><RagBadge status="Amber" /> Source Schedule Health</div>
            <p className="text-muted-foreground leading-relaxed">
              This is the value your PM manually entered in the workbook (or exported from MS Project / Primavera).
              It reflects the team's self-assessment at the time of export.
            </p>
          </div>
          <div className="space-y-1.5">
            <div className="font-semibold flex items-center gap-2"><RagBadge status="Red" /> Agent RAG Status</div>
            <p className="text-muted-foreground leading-relaxed">
              This is the platform's independent, deterministic conclusion based on six scored signals.
              When both values differ, leadership can see the disagreement and investigate the discrepancy.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}