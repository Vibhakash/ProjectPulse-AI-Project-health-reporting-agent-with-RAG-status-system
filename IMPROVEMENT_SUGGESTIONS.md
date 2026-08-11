# ProjectPulse AI — Improvement Suggestions

This document lists potential feature enhancements for ProjectPulse AI, ranked by impact. Review each suggestion and indicate whether you'd like it implemented.

---

## High Priority — Strongly Recommended

### 1. Multi-Snapshot Trend Charts
**What:** Show a line chart of RAG score over time for each project across multiple uploads.
**Why:** Right now you can only see the current snapshot. Adding trend charts would immediately reveal if a project is improving or deteriorating over time — which is the core value of a health reporting tool.
**Effort:** Medium. Requires a new API endpoint + Recharts line chart on the project detail page.

---

### 2. Email / Notification Alerts on RAG Status Changes
**What:** When a project flips from Green to Amber or Amber to Red, send an email alert (or Slack/Teams webhook).
**Why:** Executives shouldn't have to log in to check; they need to be pushed critical alerts automatically.
**Effort:** Medium. Requires SMTP config (or a webhook URL env var) and a trigger in the analyze pipeline.

---

### 3. Portfolio-Level Summary Dashboard Improvements
**What:** Add a donut/pie chart for RAG distribution and a sortable/filterable project table with column headers (score, DQ, confidence, stage).
**Why:** The current portfolio page is a flat list. A proper data grid with sorting and the donut chart would make it much more useful for a PM or executive reviewing 10+ projects.
**Effort:** Low-Medium. Mostly frontend work using Recharts.

---

### 4. PDF Export of Weekly Report
**What:** Add an "Export as PDF" button next to each project's snapshot detail that generates a clean, printable PDF report.
**Why:** The monthly PPTX is great for executives but PMs often need a per-project PDF they can attach to stakeholder emails.
**Effort:** Medium. Use `reportlab` or `weasyprint` on the backend to render the Markdown report as PDF.

---

## Medium Priority — Nice to Have

### 5. Baseline Date & Variance Auto-Calculation
**What:** If Baseline Start/Finish is missing but Start/End is provided, auto-estimate variance using a simple rule.
**Why:** Many real-world project plans don't include baseline columns. The system currently degrades the score rather than making a reasonable estimate.
**Effort:** Low. Logic change in `normalizer.py` and `rag_engine.py`.

---

### 6. Multi-Language Support for Project Plan Comments
**What:** Detect the language of PM comments and translate them to English before sentiment analysis.
**Why:** Global teams often write comments in Hindi, Spanish, or German. The current sentiment engine works best on English text.
**Effort:** Medium. Add a translation step using the LLM (a single prompt) before passing to the sentiment signal.

---

### 7. User-Defined Signal Weight Configuration via UI
**What:** Add a "Settings" page where users can adjust the 6 signal weights (e.g. reduce Budget from 5% to 0% if not used).
**Why:** Different organizations prioritize different signals. A PM focused on milestone-driven projects may want to increase Milestone Health to 40%.
**Effort:** Medium. Requires a settings UI + saving weights to a DB table + passing weights to the RAG engine per run.

---

### 8. Project Comparison View (Side-by-Side)
**What:** Let users select two projects and view them side-by-side — signals, scores, and key metrics compared in a table.
**Why:** Useful for portfolio reviews where executives want to understand why Project A is Red but Project B is Green.
**Effort:** Medium. New route with a two-column layout using existing API data.

---

### 9. "Ask Data" Query Suggestions / Auto-Complete
**What:** Show example queries below the Ask Data input box (e.g. "Which projects have a float less than 0?", "List all Red tasks").
**Why:** Users don't know what questions to ask. Suggested queries lower the barrier to using the feature.
**Effort:** Low. Pure UI change — add a row of clickable chip suggestions.

---

### 10. Snapshot Comparison / Diff View
**What:** Show what changed between two snapshots of the same project (tasks added/removed, RAG score change, signal score changes).
**Why:** After re-uploading an updated project plan, users need to see exactly what changed, not just the new snapshot in isolation.
**Effort:** Medium-High. Requires a diff computation endpoint and a visual diff UI.

---

## Low Priority — Future Roadmap

### 11. REST API Authentication (JWT / API Key)
**What:** Add proper JWT-based API authentication so the backend endpoints are protected, not just the frontend.
**Why:** Right now, anyone who knows the API URL can call `/api/analyze` without logging in.
**Effort:** Medium. Add FastAPI middleware + key storage in SQLite.

---

### 12. Bulk Upload from a Folder / ZIP
**What:** Allow users to upload a `.zip` file containing multiple `.xlsx` files for batch processing.
**Why:** Teams with 20+ projects don't want to click "add file" 20 times.
**Effort:** Low-Medium. Extract ZIP in a temp dir and iterate over `.xlsx` files.

---

### 13. Gantt Chart View per Project
**What:** Render a simple Gantt chart from task Start/End dates in the Task Evidence tab.
**Why:** PMs are used to seeing Gantt charts and it makes the task hierarchy immediately visible.
**Effort:** High. Requires a charting library like `gantt-task-react` or a custom SVG renderer.

---

### 14. Dark/Light Theme Per-User Preference Saved
**What:** Save the user's theme preference to localStorage so it persists across browser sessions.
**Why:** The toggle works per-session but resets on reload.
**Effort:** Very Low. Save to localStorage in the theme hook.

---

### 15. Webhook Integration (Jira / Azure DevOps)
**What:** Pull task data directly from Jira or Azure DevOps via API instead of requiring an Excel upload.
**Why:** Eliminates the manual export step for teams already using these tools.
**Effort:** Very High. Requires OAuth integration and field mapping for each tool.

---

> **How to use this list:** Review each suggestion above and let me know which ones you'd like implemented. I'll prioritize based on your feedback and build them in order.
