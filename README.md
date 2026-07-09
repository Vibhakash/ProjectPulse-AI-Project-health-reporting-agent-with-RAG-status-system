# Project Health Reporting Agent with RAG Status System

An intelligent project health reporting and RAG synthesis agent. It parses multi-sheet Excel project schedules, computes deterministic RAG status scores, layers LLM-derived stakeholder sentiment analysis and narrative summaries, and presents findings in a modern React dashboard and widescreen executive PowerPoint deck.

---

## 📦 Deliverables Map

The files required for submission are prepared at the following locations in the workspace:

1.  **One-Page RAG Methodology**:
    *   File Path: [`docs/rag_methodology.md`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/docs/rag_methodology.md)
    *   Also browseable directly in the web dashboard under the **"How Project Works"** page.
2.  **Working AI Agent (Code + Instructions)**:
    *   Instructions to run both frontend and backend are detailed below.
3.  **Sample Weekly Outputs**:
    *   **Green Project**: [`outputs/weekly/zycus-green-implementation_2026-07-08.md`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-green-implementation_2026-07-08.md) (and [`.json`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-green-implementation_2026-07-08.json))
    *   **Amber Project**: [`outputs/weekly/zycus-amber-implementation_2026-07-08.md`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-amber-implementation_2026-07-08.md) (and [`.json`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-amber-implementation_2026-07-08.json))
    *   **Red Project**: [`outputs/weekly/zycus-red-implementation_2026-07-08.md`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-red-implementation_2026-07-08.md) (and [`.json`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/weekly/zycus-red-implementation_2026-07-08.json))
4.  **Final Monthly Presentation (5–7 Slides)**:
    *   File Path: [`outputs/monthly/monthly_project_health.pptx`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/outputs/monthly/monthly_project_health.pptx) (Exactly **6 slides** total, generated in widescreen 16:9 layout).
5.  **Verification & Supporting Documents (PDF and Word formats)**:
    *   Methodology: PDF [`docs/rag_methodology.pdf`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/docs/rag_methodology.pdf) | Word [`docs/rag_methodology.docx`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/docs/rag_methodology.docx)
    *   Requirements Fulfilled Guide: PDF [`docs/requirements_and_deliverables.pdf`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/docs/requirements_and_deliverables.pdf) | Word [`docs/requirements_and_deliverables.docx`](file:///c:/Users/Vibha/Desktop/vibha/Projects/Zycus%20Project-Project%20health%20reporting%20agent%20with%20RAG%20status%20system/docs/requirements_and_deliverables.docx)

---

## 🛠️ Setup & Running

Both backend and frontend services are currently active in the background. If you need to restart them, use the following steps:

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### Setup Environment
1.  **Backend Setup**:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    pip install -e .
    ```
2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

### Run Servers
*   **Terminal 1 — Backend FastAPI Server (runs on Port 8001)**:
    ```bash
    .venv\Scripts\scripts\python run_api.py
    ```
*   **Terminal 2 — Frontend Dev Server (runs on Port 3000)**:
    ```bash
    cd frontend
    npm run dev
    ```
Open **[http://localhost:3000](http://localhost:3000)** in your browser to view the application.

---

## Design Decisions & Architecture

### 1. Deterministic RAG First, LLM Second
The project separates factual scoring from narrative generation. The final Red, Amber, or Green status is calculated by a deterministic weighted rule engine in `src/project_health/rag_engine.py`, rather than asking an LLM to infer project health directly from spreadsheets.

This was intentional because executive status reporting needs traceability. The scoring model uses inspectable signals such as schedule health, progress gap, milestone health, blockers, stakeholder sentiment, and budget availability. The LLM layer is used only after these signals are computed, turning the evidence into executive summaries, risk themes, and next-step recommendations.

### 2. Evidence-Based Reporting
The system preserves source row numbers, parsed task details, comments, warnings, and signal-level reasoning. This makes each RAG decision auditable instead of being a black-box summary.

SQLite is used as the persistence layer because it is lightweight, portable, and easy for reviewers to inspect. It stores project snapshots, tasks, comments, RAG signals, and data quality issues so that weekly reports and monthly synthesis can be regenerated from the same evidence base.

### 3. Resilient Excel Ingestion
The Excel parser is designed for messy project-plan exports. It detects useful sheets and columns from workbook content, normalizes inconsistent field names, handles missing or malformed values, reconstructs WBS hierarchy from level/ancestor fields, and reduces confidence when important evidence is unavailable.

This avoids overfitting the agent to one perfect template and makes it more realistic for operational project reporting, where exported workbooks often contain blanks, optional columns, locked files, or inconsistent headers.

### 4. Portfolio-Level Monthly Synthesis
The monthly PowerPoint is intentionally limited to a concise executive deck instead of creating one slide per project. `src/project_health/monthly_synthesis.py` consolidates project health into a portfolio summary, project directory, narrative and sentiment themes, systemic risks, leadership actions, and methodology explanation.

This design keeps the output useful for leadership review: the deck highlights cross-project patterns and decisions needed, while detailed weekly Markdown/JSON reports remain available for project-level drilldown.

### 5. Frontend and Backend Separation
The backend owns ingestion, scoring, persistence, report generation, and synthesis. The React frontend focuses on uploading project plans, browsing portfolio health, viewing methodology, asking project-health questions, and navigating generated insights.

This split keeps the analytical logic reusable from CLI, API, scheduler, or dashboard workflows.

---

## Demo Video Availability

The demo video `Zycus-ProjectPulse AI-by Vibha Kashyap.mp4` is available in the local project folder.

It is intentionally not committed to GitHub because the file is about 172 MB, which exceeds GitHub's regular 100 MB per-file limit. The repository contains the complete source code, documentation, sample inputs, generated docs, and runnable application files; the video should be shared separately or uploaded through Git LFS or external storage if required.
