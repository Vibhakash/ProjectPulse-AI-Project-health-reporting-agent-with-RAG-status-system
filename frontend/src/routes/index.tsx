import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/button";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  CheckCircle2,
  FileSpreadsheet,
  Gauge,
  LineChart,
  Moon,
  ShieldCheck,
  Sparkles,
  Sun,
  Upload,
} from "lucide-react";
import heroImg from "@/assets/hero.jpg";
import analyticsImg from "@/assets/analytics.jpg";
import leadershipImg from "@/assets/leadership.jpg";

export const Route = createFileRoute("/")({
  component: Branding,
});

function Branding() {
  const { theme, toggle } = useTheme();
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSignedIn(!!data.session));
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => setSignedIn(!!s));
    return () => sub.subscription.unsubscribe();
  }, []);

  const primaryCta = signedIn ? { to: "/portfolio", label: "Open dashboard" } : { to: "/auth", label: "Sign in to start" };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Top nav */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Activity className="h-4.5 w-4.5" />
            </span>
            <span className="text-sm font-semibold tracking-tight">ProjectPulse AI</span>
          </Link>
          <nav className="ml-6 hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <a href="#product" className="hover:text-foreground">Product</a>
            <a href="#how" className="hover:text-foreground">How it works</a>
            <a href="#features" className="hover:text-foreground">Features</a>
            <a href="#trust" className="hover:text-foreground">Trust</a>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Button variant="ghost" size="icon" aria-label="Toggle theme" onClick={toggle}>
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            {signedIn ? (
              <Button asChild size="sm">
                <Link to="/portfolio">Open dashboard</Link>
              </Button>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm">
                  <Link to="/auth">Sign in</Link>
                </Button>
                <Button asChild size="sm">
                  <Link to="/auth" search={{ mode: "signup" }}>Get started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-hero-radial">
        <div className="absolute inset-0 bg-grid opacity-30 pointer-events-none" />
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 md:py-24 lg:grid-cols-[1.05fr_1fr] lg:items-center">
          <div className="animate-fade-up">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <Sparkles className="h-3.5 w-3.5" />
              Executive project intelligence
            </span>
            <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Automated project health intelligence for{" "}
              <span className="bg-gradient-to-r from-primary to-rag-green bg-clip-text text-transparent">
                faster leadership decisions
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-base text-muted-foreground sm:text-lg">
              Upload weekly project plans. ProjectPulse AI parses schedules, tasks, comments and baselines,
              then derives a transparent RAG status with the exact evidence behind every score.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg" className="gap-2">
                <Link to={primaryCta.to}>
                  {primaryCta.label} <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <a href="#how">See how it works</a>
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap gap-6 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-rag-green" /> Deterministic scoring</span>
              <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-rag-green" /> Full evidence trail</span>
              <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-rag-green" /> Weekly + monthly reports</span>
            </div>
          </div>

          <div className="relative animate-fade-up [animation-delay:120ms]">
            <div className="absolute -inset-6 rounded-3xl bg-gradient-to-tr from-primary/30 via-transparent to-rag-green/25 blur-2xl" />
            <div className="relative overflow-hidden rounded-2xl border border-border/60 shadow-2xl">
              <img
                src={heroImg}
                alt="ProjectPulse AI executive dashboard preview"
                width={1600}
                height={1000}
                className="w-full h-auto"
              />
            </div>
            {/* Floating RAG chips */}
            <div className="absolute -bottom-4 -left-4 animate-float glass-card rounded-xl p-3 text-xs shadow-lg">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-rag-red animate-pulse-ring" />
                <span className="font-medium">3 Red</span>
                <span className="h-2.5 w-2.5 rounded-full bg-rag-amber ml-2" />
                <span className="font-medium">5 Amber</span>
                <span className="h-2.5 w-2.5 rounded-full bg-rag-green ml-2" />
                <span className="font-medium">12 Green</span>
              </div>
            </div>
            <div className="absolute -top-4 -right-4 animate-float [animation-delay:1.5s] glass-card rounded-xl p-3 text-xs shadow-lg">
              <div className="flex items-center gap-2"><Gauge className="h-4 w-4 text-primary" /> Confidence: Medium</div>
            </div>
          </div>
        </div>
      </section>

      {/* Product */}
      <section id="product" className="mx-auto max-w-7xl px-4 py-16">
        <div className="grid gap-10 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <h2 className="text-3xl font-bold tracking-tight">Built for PS leadership</h2>
            <p className="mt-3 text-muted-foreground">
              Stop chasing PMs for updates. Turn raw Excel project plans into a portfolio-wide health picture in minutes.
            </p>
          </div>
          <div className="lg:col-span-2 grid gap-4 sm:grid-cols-2">
            {[
              { icon: Upload, title: "Ingest any project plan", body: "Multi-sheet .xlsx workbooks parsed into a normalized schedule model." },
              { icon: Brain, title: "Deterministic RAG engine", body: "Weighted signals with full audit trail — no LLM guesswork on status." },
              { icon: BarChart3, title: "Portfolio at a glance", body: "One dashboard for every active engagement, ranked by risk." },
              { icon: FileSpreadsheet, title: "Reports on autopilot", body: "Weekly Markdown + JSON per project, monthly executive PPTX." },
            ].map(({ icon: Icon, title, body }) => (
              <div key={title} className="glass-card rounded-xl p-5">
                <Icon className="h-5 w-5 text-primary" />
                <div className="mt-3 font-semibold">{title}</div>
                <p className="mt-1 text-sm text-muted-foreground">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="border-y border-border/60 bg-muted/30">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 lg:grid-cols-2 lg:items-center">
          <div className="relative">
            <img
              src={analyticsImg}
              alt="Layered analytics"
              width={1400}
              height={1000}
              loading="lazy"
              className="w-full rounded-2xl border border-border/60 shadow-xl"
            />
          </div>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">How it works</h2>
            <ol className="mt-6 space-y-5">
              {[
                { n: "01", t: "Upload project plans", d: "Drop one or more .xlsx workbooks. We preserve every task attribute in an audit-ready store." },
                { n: "02", t: "Run analysis", d: "The rule engine scores each project using weighted signals — schedule variance, critical path, blockers, comments, quality." },
                { n: "03", t: "Review evidence", d: "Every RAG decision links back to the exact source rows, baselines, and PM commentary." },
                { n: "04", t: "Download reports", d: "Weekly Markdown/JSON per project. Monthly PPTX for the executive committee." },
              ].map((s) => (
                <li key={s.n} className="flex gap-4">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/15 text-sm font-semibold text-primary">
                    {s.n}
                  </div>
                  <div>
                    <div className="font-semibold">{s.t}</div>
                    <p className="text-sm text-muted-foreground">{s.d}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      {/* Features grid */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-16">
        <h2 className="text-3xl font-bold tracking-tight text-center">Everything leadership needs, nothing they don't</h2>
        <p className="mt-3 text-center text-muted-foreground max-w-2xl mx-auto">
          A focused workspace: upload, portfolio, evidence, reports, and a natural-language query — no bloat.
        </p>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Gauge, title: "RAG status per project", body: "Red / Amber / Green with score, confidence and data quality." },
            { icon: LineChart, title: "Signal breakdown", body: "See exactly which signals drove the RAG and how they were weighted." },
            { icon: FileSpreadsheet, title: "Task evidence", body: "Filterable task table with critical path, float, variance, owners." },
            { icon: Brain, title: "Ask your project data", body: "Query blockers, red projects and dependencies in plain language." },
            { icon: ShieldCheck, title: "Honest empty states", body: "No mock metrics. If data isn't there, we say so." },
            { icon: Sparkles, title: "Monthly executive deck", body: "One-click PPTX for board and steering committee." },
          ].map(({ icon: Icon, title, body }) => (
            <div key={title} className="rounded-xl border border-border/60 bg-card p-5 hover:border-primary/40 transition-colors">
              <Icon className="h-5 w-5 text-primary" />
              <div className="mt-3 font-semibold">{title}</div>
              <p className="mt-1 text-sm text-muted-foreground">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Trust */}
      <section id="trust" className="border-t border-border/60 bg-muted/30">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 lg:grid-cols-2 lg:items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Transparent. Data-driven. Auditable.</h2>
            <p className="mt-3 text-muted-foreground">
              ProjectPulse AI never invents metrics. RAG decisions come from a deterministic rule engine with a
              recorded audit trail — every score can be traced to the source rows in your workbook.
            </p>
            <ul className="mt-6 space-y-2 text-sm">
              {[
                "Weighted signal scoring with configurable weights (backend-managed).",
                "Source schedule health shown alongside agent-derived RAG.",
                "Full evidence list per signal — no black-box status.",
                "Preserves every column of your source workbook.",
              ].map((t) => (
                <li key={t} className="flex gap-2"><CheckCircle2 className="h-4 w-4 text-rag-green mt-0.5" /> {t}</li>
              ))}
            </ul>
          </div>
          <img
            src={leadershipImg}
            alt="Leadership team reviewing project health"
            width={1400}
            height={900}
            loading="lazy"
            className="w-full rounded-2xl border border-border/60 shadow-xl"
          />
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 py-20 text-center">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Ready to see your portfolio's real health?
        </h2>
        <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
          Sign in to upload a project plan and get your first RAG snapshot in minutes.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Button asChild size="lg" className="gap-2">
            <Link to={primaryCta.to}>
              {primaryCta.label} <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      <footer className="border-t border-border/60">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <div>© {new Date().getFullYear()} ProjectPulse AI</div>
          <div className="flex items-center gap-4">
            <a href="#product" className="hover:text-foreground">Product</a>
            <a href="#how" className="hover:text-foreground">How it works</a>
            <Link to="/auth" className="hover:text-foreground">Sign in</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
