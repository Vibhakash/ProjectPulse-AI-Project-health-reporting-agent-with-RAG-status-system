# Project Health Reporting Agent - Requirements Coverage

This document compares the Zycus assignment expectations with the implemented backend project.

## Overall Status

The backend implementation satisfies the core assignment requirements:

- Defines a transparent RAG methodology.
- Reads real Excel project plans.
- Handles messy and incomplete data.
- Derives RAG status independently from workbook-provided health columns.
- Explains the RAG decision with evidence.
- Generates weekly project outputs.
- Persists snapshots in SQLite for trend tracking.
- Generates a monthly executive PowerPoint deck.

No frontend is included yet. Frontend work is intentionally deferred until approved.

## Requirements Coverage

| Assignment Expectation | Implemented? | Where / How |
|---|---:|---|
| One-page RAG methodology | Yes | `docs/rag_methodology.md` |
| Read project plans | Yes | `.xlsx` ingestion in `src/project_health/excel_reader.py` and `src/project_health/normalizer.py` |
| Handle different project plan schemas | Yes | Sheet detection and field alias mapping in `config.py` / `normalizer.py` |
| Preserve all sheet attributes | Yes | Typed task fields plus `raw_data_json` stored in SQLite |
| Handle messy data gracefully | Yes | `#UNPARSEABLE`, blank fields, date parsing issues, missing comments, and missing budget are flagged as data quality issues |
| Determine RAG status | Yes | Deterministic scoring engine in `src/project_health/rag_engine.py` |
| Do not blindly copy existing RAG/Schedule Health | Yes | Existing `Schedule Health` is stored as source evidence only; final RAG is independently derived |
| Explain RAG reasoning in plain English | Yes | `src/project_health/reasoning.py` and weekly report generation |
| Schedule slippage considered | Yes | Schedule health, dates, late tasks, baseline/variance/float where available |
| Budget burn considered | Partially / honestly unavailable | Budget is supported only if workbook columns exist. Provided files do not contain budget fields, so reports state budget is unavailable |
| Milestone health considered | Yes | Phase/milestone rows are scored separately |
| Blockers considered | Yes | Critical active tasks, on-hold flags, negative float, status comments, and blocker keywords |
| Stakeholder sentiment considered | Yes | Comments sheet and status comments are scanned; empty comments reduce confidence instead of inventing sentiment |
| Weekly outputs for each project | Yes | `outputs/weekly/*.md` and `outputs/weekly/*.json` |
| Monthly 5-7 slide executive presentation | Yes | `outputs/monthly/monthly_project_health.pptx` generated via `python-pptx` |
| Identify trends across projects | Yes | SQLite snapshots support trend tracking; deck includes portfolio view, RAG movement, risk themes, and recommendations |
| Highlight emerging risks | Yes | Top risk tasks, signal evidence, blocker themes, and recommendations |
| Executive-level recommendations | Yes | Weekly reports and monthly deck include recommended actions |
| Runnable on weekly schedule | Yes | Scheduler entry point exists in `src/project_health/scheduler.py` / CLI `schedule` command |
| README / instructions | Yes | `README.md` |
| Tests | Yes | `tests/` with pytest coverage |

## Implemented Features

### Data Ingestion And Normalization

- Reads `.xlsx` files.
- Supports multiple workbook schemas.
- Detects task, comments, and summary sheets.
- Handles `S2P Project.xlsx` and `Project Plan B.xlsx`.
- Reconstructs task hierarchy from `Level` and `Ancestors`.
- Preserves source row numbers for evidence traceability.
- Stores all original task columns in SQLite as raw JSON.

### SQLite Persistence

The backend stores project history in SQLite.

Tables:

- `projects`
- `project_snapshots`
- `tasks`
- `comments`
- `rag_signals`
- `data_quality_issues`

This allows weekly snapshots, audit trails, and trend analysis.

### RAG Engine

The RAG engine is deterministic and explainable.

Signals:

- Schedule health
- Progress vs expected timeline
- Milestone health
- Blockers / on-hold / critical-path risk
- Stakeholder sentiment from comments
- Budget burn, only when budget fields exist

The final status is based on weighted scoring and critical override rules.

### Explainability

Each RAG decision stores:

- Signal name
- Signal weight
- Raw signal value
- Normalized score
- Weighted score
- Evidence
- Override flag

This makes the agent auditable and avoids black-box RAG decisions.

### Weekly Reports

Generated per project:

- Markdown report
- JSON report

Each report includes:

- RAG status
- Risk score
- Confidence
- Data quality score
- Source schedule health comparison
- Reasons
- Signal breakdown
- Top risks
- Recommended actions
- Data caveats
- Preserved workbook attributes

### Monthly Executive Deck

Generated as:

- `outputs/monthly/monthly_project_health.pptx`

Slides include:

- Title and reporting period
- Portfolio health overview
- Trend themes
- Emerging risks
- Executive recommendations
- Methodology / assumptions appendix

### Query Capability

The backend includes a simple query command over SQLite:

```powershell
.venv\Scripts\python -m project_health.cli ask --db storage/project_health.sqlite "Which projects have external dependency blockers?"
```

This is not a full chatbot. It is a lightweight project-data query feature.

## Tech Stack Used

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.12 locally, Python 3.11+ compatible | Backend implementation |
| Excel ingestion | `openpyxl`, fallback OOXML parser | Read multi-sheet `.xlsx` files |
| Data handling | Standard Python dataclasses | Internal normalized schemas |
| Database | SQLite | Portable local persistence |
| DB access | `sqlite3` standard library | Lightweight database access |
| RAG engine | Deterministic Python rule engine | Transparent project health scoring |
| Config | JSON | RAG weights and keyword configuration |
| Reports | Markdown + JSON | Weekly outputs |
| Presentation | `python-pptx` | Monthly executive PowerPoint generation |
| Charts support | `matplotlib` | Available for deck/chart extension |
| Scheduling | `APScheduler` / CLI loop | Weekly run support |
| CLI | `argparse` | Command-line backend operation |
| Testing | `pytest` | Backend verification |
| Packaging | `pyproject.toml`, `requirements.txt` | Reviewer setup and installability |
| Environment | `.venv` | Isolated dependency installation |

## API Key Status

No API key is required for the current implementation.

The backend currently uses deterministic offline reasoning. It does not call:

- OpenAI
- Claude
- LangChain
- LangGraph
- Any external LLM API

An LLM layer can be added later for richer language generation or comment clustering, but the working submission does not depend on API keys.

## Verified Outputs

The backend has been verified with the provided sample Excel plans.

Generated files:

- `outputs/weekly/zycus-unisan-s2p-implementation_2026-07-08.md`
- `outputs/weekly/zycus-unisan-s2p-implementation_2026-07-08.json`
- `outputs/weekly/zycus-titan-s2p-implementation_2026-07-08.md`
- `outputs/weekly/zycus-titan-s2p-implementation_2026-07-08.json`
- `outputs/monthly/monthly_project_health.pptx`

Verified test command:

```powershell
.venv\Scripts\python -m pytest -q
```

Result:

```text
4 passed
```

## Known Limitations

- Budget burn cannot be scored from the provided files because no budget/cost/burn columns exist.
- Stakeholder sentiment is limited when a workbook has an empty Comments sheet.
- Trend analysis becomes stronger after multiple weekly snapshots; with only one run per project, trend movement is naturally limited.
- Current system is backend/CLI-first. A REST API wrapper can be added when integrating with a frontend.

## Conclusion

The implementation meets the main company requirements for the assignment. It provides a working, auditable backend agent that reads real project plans, determines RAG status, explains the reasoning, handles messy data, generates weekly outputs, and creates an executive monthly presentation.

