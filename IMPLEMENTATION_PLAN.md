# Project Health Reporting Agent - Backend Implementation Plan

## Current Inputs Reviewed

- Assignment requires:
  - One-page RAG methodology.
  - Working agent that reads project plans, determines RAG, explains reasoning, and handles messy data.
  - Weekly outputs per project.
  - Monthly 5-7 slide executive synthesis.
  - README or short design explanation.
- `Features and techstack.txt` has been reviewed and merged into this backend plan.
- Sample workbooks observed:
  - `S2P Project.xlsx`: main project sheet, `Comments`, `Summary`.
  - `Project Plan B.xlsx`: `Project Plan`, `Comments`, `Summary`.
  - Both are hierarchical WBS exports using fields like `Level` and/or `Ancestors` to represent project -> phase -> milestone -> task relationships.
  - Common useful fields: project manager, phase/milestone, schedule health, task name, status, percent complete, dates, baseline dates, variance, total float, critical flag, status comments, summary stage, summary at-risk value.
  - Some fields are messy or missing: `#UNPARSEABLE` cells, blank project names, optional date/baseline columns, empty comments in one workbook, no explicit budget columns.
  - The existing `Schedule Health`/RAG-like column should be treated as a comparison signal only. The agent must derive its own RAG independently and can show whether it agrees or disagrees with the existing PM/system value.

## Backend Scope Only

No frontend work will start until this file is approved.

The first implementation will be a command-line/backend system that can:

1. Read Excel project plans from an input folder.
2. Normalize messy project plan data into a consistent internal schema.
3. Reconstruct project hierarchy from WBS fields like `Level` and `Ancestors`.
4. Persist projects, tasks, comments, snapshots, and RAG audit signals in SQLite.
5. Calculate deterministic health metrics.
6. Use an AI reasoning layer to produce plain-English explanations from those metrics.
7. Generate weekly Markdown/JSON reports for each project.
8. Generate a monthly executive PowerPoint from all stored project outputs.
9. Optionally run on a weekly schedule using a simple scheduler entry point.

## Recommended Tech Stack

- Language: Python 3.11+
- Excel parsing: `pandas`, `openpyxl`
- Database: SQLite via `SQLAlchemy`
- Validation/schema: `pydantic`
- AI layer: OpenAI or Claude API with structured JSON output, plus local fallback template mode
- Reports:
  - Markdown for human-readable weekly reports.
  - Optional PDF export after Markdown generation.
  - JSON for reusable structured outputs.
  - `python-pptx` for the final executive presentation.
- CLI: `typer`
- Charts: `matplotlib` for trend visuals embedded into executive slides.
- Scheduling: `APScheduler` for local weekly runs, plus a Windows Task Scheduler/GitHub Actions example in README.
- Testing: `pytest`
- Packaging: `requirements.txt`, `.env.example`, and optional `Dockerfile`.

## Backend Folder Structure

```text
project-health-agent/
  src/
    project_health/
      __init__.py
      cli.py
      config.py
      db.py
      excel_reader.py
      normalizer.py
      metrics.py
      rag_engine.py
      reasoning.py
      repositories.py
      report_writer.py
      monthly_synthesis.py
      scheduler.py
      models.py
      schemas.py
      charts.py
  config/
    rag_weights.yaml
  data/
    input/
    sample_outputs/
  storage/
    project_health.sqlite
  outputs/
    weekly/
    monthly/
  docs/
    rag_methodology.md
  tests/
    test_normalizer.py
    test_metrics.py
    test_rag_engine.py
    test_repository.py
  README.md
  requirements.txt
  .env.example
  Dockerfile
```

## Data Normalization Plan

The backend should not rely on exact sheet names or perfect headers. It will:

- Detect the main task sheet by looking for columns like `Task Name`, `Status`, `% Complete`, `Schedule Health`.
- Detect the summary sheet by keys like `Project Manager`, `Project Start Date`, `Project End Date`, `At Risk`, `Project Stage`.
- Detect comments by row references and comment text.
- Map variant column names through a config-driven column mapping layer instead of relying on hardcoded positions.
- Reconstruct the WBS hierarchy using `Level`, `Ancestors`, and row order, then persist parent-child relationships.
- Convert Excel serial dates into normal dates when present.
- Convert `% Complete` values like `0.71` into `71%`.
- Clean values like `#UNPARSEABLE`, blanks, missing dates, odd negative variance values, and malformed numbers into explicit `unknown` values with warnings.
- Preserve source row numbers for traceability.
- Preserve the workbook's existing `Schedule Health` value as `source_schedule_health` for sanity checks, but do not copy it as the final agent RAG.

## SQLite Persistence Plan

SQLite will be the backend database because it is portable, reviewer-friendly, and enough for the assignment's weekly snapshot workflow.

Proposed tables:

- `projects`: one row per detected project/workbook identity.
- `project_snapshots`: one row per project per run date, including final RAG, score, confidence, stage, summary metrics, and output file paths.
- `tasks`: normalized task/milestone rows with hierarchy fields, status, completion, dates, baseline dates, variance, float, critical flag, schedule health, and source row.
- `comments`: timestamped free-text comments linked to project/task rows when possible.
- `rag_signals`: audit table storing each signal, weight, raw value, normalized score, evidence references, and whether it triggered an override.
- `data_quality_issues`: parsing and completeness warnings per workbook/run.

This gives the submission a real time series for trend detection instead of only one-off file outputs.

## RAG Methodology

The agent should calculate a weighted risk score from available signals. Missing signals should reduce confidence, not automatically punish the project.

Proposed scoring:

| Signal | Weight | Green | Amber | Red |
|---|---:|---|---|---|
| Schedule health | 30% | Most active/milestone tasks green | Meaningful yellow share or some late tasks | Red tasks, severe delay, or critical milestone red |
| Progress vs plan | 20% | Completion broadly matches elapsed timeline | 10-20% behind expected progress | More than 20% behind expected progress |
| Milestone health | 20% | Key milestones completed/on track | Upcoming milestone risk or partial slippage | Blocked/late critical milestone |
| Blockers/on-hold/risk flags | 15% | No major blockers | Some on-hold/risk items | Multiple high-risk/on-hold/blocker items |
| Stakeholder sentiment/comments | 10% | Comments neutral/positive/resolved | Dependency or follow-up concerns | Repeated unresolved blockers/escalations |
| Budget burn | 5% | Available and within plan | Mild variance | Severe variance |

Detailed signal extraction:

- Schedule slippage:
  - Prefer baseline vs actual/current dates, variance columns, total float, and critical-path markers when available.
  - Fall back to start/end dates, elapsed project time, remaining work, and existing row-level schedule health when baseline fields are absent.
- Progress vs plan:
  - Compare percent complete against expected progress from project elapsed time.
  - Flag large gaps between completion and elapsed timeline.
- Milestone health:
  - Score phase/milestone-level rows separately from leaf tasks.
  - Use hierarchy to avoid over-weighting many child tasks under the same troubled milestone.
- Blockers:
  - Use `Critical?`, negative `Total Float`, `On Hold?`, high-risk flags, and blocker keywords in status comments.
- Stakeholder sentiment:
  - Use the Comments sheet and status comments.
  - If comments are empty, report "no stakeholder sentiment data available" and reduce confidence.
- Budget burn:
  - Only score when budget/burn/cost fields are present.
  - Exclude from score and document as unavailable for the provided samples.

Budget handling assumption:

- The sample files do not expose budget/burn fields.
- Budget will be marked `unknown` and excluded from scoring unless future workbooks include budget columns.
- The report will state that budget confidence is unavailable rather than inventing a conclusion.

Final status:

- Green: score below 35 and no red critical override.
- Amber: score 35-69 or medium confidence with notable risks.
- Red: score 70+ or critical override, such as project-level schedule health red, summary `At Risk = High` with red schedule, or critical milestone blocked.

Critical override examples:

- Project-level source schedule health is red and independent signals also show major slippage.
- Critical milestone is incomplete, late, or has negative float.
- Multiple blocker comments indicate unresolved external dependency or client data delay.
- Summary says `At Risk = High` and schedule/progress signals are amber or red.

Confidence:

- High: schedule, status, completion, milestones, and comments/summary available.
- Medium: core task data available but dates/comments/budget incomplete.
- Low: missing most core fields or data quality warnings dominate.

The agent should also calculate a data quality score based on expected field availability and parsing issues. This score appears in reports and is stored in SQLite.

## AI Reasoning Layer

The AI should not decide the RAG color from raw spreadsheets alone. The deterministic engine will calculate metrics first; the AI layer will convert those metrics into executive-friendly reasoning.

Prompt inputs:

- Normalized project summary.
- Key metrics and RAG score.
- Top risky tasks/milestones.
- Recent blocker/comment themes.
- Existing source schedule health comparison.
- Data quality warnings.

Prompt outputs:

- RAG status.
- 3-5 plain-English reasons.
- Top risks.
- Recommended next actions.
- Data caveats.
- Evidence references, such as source sheet and row number where possible.

Fallback mode:

- If no API key is configured, generate a deterministic template report from metrics so the assignment still runs.

## Weekly Output Format

For each workbook:

- `outputs/weekly/<project_slug>_<date>.md`
- `outputs/weekly/<project_slug>_<date>.json`
- Optional: `outputs/weekly/<project_slug>_<date>.pdf`

Each run will also write a snapshot and signal audit rows to SQLite.

Weekly report sections:

- Executive summary.
- RAG status and confidence.
- Why this status.
- Schedule and milestone indicators.
- Blockers and comments.
- Data quality notes.
- Source schedule health vs agent-derived RAG comparison.
- Recommended actions for the next week.

## Monthly Synthesis Plan

Generate `outputs/monthly/monthly_project_health.pptx` with 5-7 slides from SQLite snapshots and weekly outputs:

1. Title and reporting period.
2. Portfolio health overview with RAG distribution.
3. Trend themes across projects, including RAG movement over time where snapshots exist.
4. Emerging risks and recurring dependency themes.
5. Notable project highlights and outliers only, not a summary of every project.
6. Executive recommendations.
7. Appendix or project-level detail, if needed.

The synthesis should compare projects instead of listing them one by one. For example:

- One project may be in configuration/build with high completion but integration dependencies.
- Another may be in training with lower completion and red schedule health.
- Comments can reveal repeated dependency themes like mapping, workshop timing, or client-provided data.
- Trend charts from SQLite snapshots can be embedded using `matplotlib`.

## Unique Features Worth Adding

These are backend-friendly features that can make the submission stronger:

- Data quality score: shows whether the RAG is based on complete evidence or partial/messy data.
- Evidence traceability: every major reason links back to source sheet, row number, or summary field.
- Explainability audit trail: SQLite `rag_signals` table records exactly which signals fired, their weights, evidence, and override behavior.
- Critical override rules: prevents a project from appearing green when a project-level red schedule or high-risk summary exists.
- Risk theme extraction: groups comments into themes such as data dependency, integration mapping, workshop delay, pending approval.
- RAG-flip alerts: flag projects that moved Green -> Amber/Red or Amber -> Red since the previous snapshot.
- Action recommender: converts risks into concrete next steps for PMs and leadership.
- Natural-language query layer over SQLite: optional CLI command for questions like "which projects are blocked on external data?"
- Offline demo mode: runs without an AI key using deterministic reasoning templates.
- Configurable weights in YAML: lets reviewers inspect and tune the RAG model without code changes.
- Weekly scheduler stub: demonstrates production readiness without adding infrastructure complexity.
- Optional Dockerfile: supports one-command reviewer setup.

Deferred frontend items:

- A Streamlit dashboard is useful later, but it is intentionally excluded until frontend work is approved.

## Implementation Steps After Approval

1. Scaffold Python backend structure and dependencies.
2. Add SQLite schema, SQLAlchemy models, and repository functions.
3. Build Excel reader and sheet/column detection.
4. Build normalization models, hierarchy reconstruction, and data quality warnings.
5. Persist projects, tasks, comments, and weekly snapshots.
6. Implement deterministic metric and RAG scoring engine with YAML-configured weights.
7. Store explainability rows in the `rag_signals` audit table.
8. Implement AI/template reasoning generator.
9. Generate weekly Markdown, JSON, and optional PDF outputs for both sample plans.
10. Generate monthly PowerPoint synthesis with portfolio trends and charts.
11. Add tests for messy input, missing fields, database persistence, RAG thresholds, and report generation.
12. Write README run instructions, assumptions, limitations, and one-page RAG methodology.

## Commands Expected After Implementation

```bash
pip install -r requirements.txt
python -m project_health.cli analyze --input data/input --output outputs --db storage/project_health.sqlite
python -m project_health.cli synthesize --db storage/project_health.sqlite --output outputs/monthly
python -m project_health.cli schedule --input data/input --output outputs --db storage/project_health.sqlite --day monday --time 09:00
python -m project_health.cli ask --db storage/project_health.sqlite "Which projects have external dependency blockers?"
```

## Approval Gate

Frontend remains paused. After this backend implementation plan is approved, backend development can begin.
