# ProjectPulse AI: Features & Tech Stack

## What's actually in the files
Both input files are hierarchical WBS exports (Project → Phase → Milestone → Task) using Level/Ancestors to nest tasks, with % Complete, Start/End Date, Baseline Start/Finish, Variance, Total Float, Critical?, Status Comment, and an existing RAG/Schedule Health column already populated per row.

- There's a separate **Comments sheet** with free-text, timestamped PM notes (this is the best raw signal for "blockers" and "stakeholder sentiment").
- A **Summary sheet** gives project-level rollups (task counts by status, % Complete, At Risk?, Project Stage).
- The two files have different schemas — Plan B has extra columns (No. of days Until Today, Baseline Start2/Finish2) and an empty Comments sheet, S2P has 25 comment entries. The ingestion layer normalizes this without assuming identical columns.
- Real messy-data handling is included (e.g., several cells are literally the string `#UNPARSEABLE`).
- **Important Design Call:** The agent derives RAG independently from signals (not just copying the PM's manual/Smartsheet-computed rating).

---

## Must-Have Features (Phase 1 & 2)

### 1. Data Ingestion & Normalization
- Parses `.xlsx` files (`pandas`/`openpyxl`), handling multiple schemas via column-mapping configs.
- Reconstructs task hierarchy from Level/Ancestors.
- Loads into SQLite: projects, tasks, comments, snapshots (one snapshot row per weekly run, for trend tracking).
- Cleans `#UNPARSEABLE`, blank dates, and odd variances (flags rather than silently dropping).

### 2. RAG Determination Engine
Deterministic signal extraction per project:
- **Schedule slippage:** Baseline vs Actual/Variance, days until end date vs % remaining.
- **Budget burn:** (Only if a budget column exists).
- **Milestone health:** Completion rate of Phase/Milestone-level rows vs elapsed time.
- **Blockers:** Critical? = True + negative Total Float, On Hold? flags, keyword scan of Status Comment.
- **Stakeholder sentiment:** LLM sentiment pass over the Comments sheet text.

A transparent rule engine turns these into a score. An LLM call on top of the computed signals generates plain-English reasoning, citing specific tasks/comments that drove the status.

### 3. Graceful Degradation on Incomplete Data
- Missing baseline falls back to Start/End Date.
- Empty Comments sheet explicitly states "no stakeholder sentiment data available".
- Logs a per-project data completeness score (Data Quality Score) so reports are honest about confidence.

### 4. Weekly Output Generation
- Structured reports per project: RAG + score breakdown + reasoning + top risks + recommendations.
- Saves as JSON (machine-readable) and Markdown/PDF (human-readable).
- Persists each run to SQLite to build a real time-series.

### 5. Monthly Synthesis (Phase 3)
- Pulls stored weekly snapshots across projects.
- Detects trends: RAG movement over time, recurring blocker themes, portfolio-level RAG distribution.
- Auto-generates an executive deck via `python-pptx`.

### 6. Deliverable Docs
- RAG methodology write-up.
- README covering architecture, setup, assumptions, limitations.
- Sample outputs.

---

## Bonus Features Built
- **Lightweight Dashboard:** Interactive React/FastAPI web interface to browse historical RAG trends and drill into task-level detail.
- **Explainability Audit Trail:** SQLite tables log exactly which signals fired and their weights.
- **Config-Driven Thresholds:** `rag_config.yaml` allows tuning RAG cutoffs without touching code.
- **RAG-flip Alerts:** Flags any project that moved Green→Amber/Red.
- **Automated Scheduling:** APScheduler runs the agent weekly.

---

## Tech Stack

| Layer | Choice | Why |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ / TypeScript | Standard for agent/data work, modern web frontend. |
| **Ingestion** | `openpyxl` | Handles messy Excel, multi-sheet workbooks. |
| **Database** | SQLite3 | Portable, file-based, relational storage. |
| **Orchestration** | LiteLLM + FastAPI | Clean REST API serving the React frontend. |
| **LLM** | Groq / OpenAI | Reasoning generation, sentiment extraction, and summarization. |
| **Scheduling** | `APScheduler` | Weekly automated runs. |
| **Presentation** | `reportlab` / `python-pptx` | High-quality PDF and slide generation. |
| **Frontend UI** | React + Vite + TailwindCSS | Fast, beautiful, interactive web dashboard. |
