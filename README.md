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

## 🧠 Design Decisions & Architecture

### 1. Hybrid RAG Model (Deterministic + LLM)
*   **Problem**: LLMs are prone to hallucinations and lack auditing guarantees, which is unacceptable for executive RAG reporting.
*   **Solution**: RAG statuses (Red, Amber, Green) are derived by a **deterministic weighted rule engine** (`src/project_health/rag_engine.py`) using structured signal calculations (Schedule Health 30%, Progress Gap 20%, Milestones 20%, Blockers 15%, Sentiment 10%, Budget 5%). 
*   **LLM Role**: The LLM agent (`llama-3.3-70b-versatile` via Groq) acts as a reasoning layer *on top* of the computed signals, producing executive summaries, stakeholder sentiment overviews, and risk themes, while citing precise row numbers for auditability.

### 2. Slide Synthesis Consolidation
*   **Problem**: In real portfolios, generating separate detail slides for each project results in a bloated, un-presentable presentation.
*   **Solution**: Overhauled `monthly_synthesis.py` to consolidate all project insights at the portfolio level into exactly **6 slides** (Executive Summary, Directory, Narrative & Sentiment, Systemic Risks, Leadership Actions, and How Project Works) with medium font sizes, perfect grid alignments, and card containers.

### 3. Active Stage Fallback & Parser Resilience
*   **Active Stage Fallback**: If the `Project Stage` field is omitted from a workbook summary, the normalizer automatically scans task hierarchies to identify the active, incomplete project phase.
*   **Resilient File Parsing & Locking**: Resolved a Windows Excel locking issue (`WinError 32`) by reading workbooks fully in memory (disabling `read_only`) and enforcing explicit handle disposal via `try/finally` blocks with `wb.close()`.
