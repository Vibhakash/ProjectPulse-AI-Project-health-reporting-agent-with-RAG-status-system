import os
from pathlib import Path
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        # Top banner
        self.set_fill_color(18, 43, 64) # Deep Slate Blue
        self.rect(0, 0, 210, 15, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 10)
        self.set_y(3)
        self.cell(0, 10, "  PROJECTPULSE AI - SYSTEM DOCUMENTATION", ln=1, align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def create_methodology_pdf(output_path: Path):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.set_y(25)
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 12, "System Methodology & Technical Architecture", ln=1)
    
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, "Deterministic RAG Scoring Engine, Natural Language Synthesis & System Architecture", ln=1)
    pdf.ln(5)
    
    # Horizontal line
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    # 1. RAG Determination Methodology
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "1. RAG Determination Methodology", ln=1)
    pdf.ln(2)
    
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("helvetica", "", 10)
    text = (
        "The core philosophy of the system is deterministic, auditable scoring. Instead of delegating "
        "RAG classification to black-box LLMs - which are susceptible to hallucination, inconsistency, "
        "and lack mathematical validation - the RAG classification is computed via a structured rule engine. "
        "The LLM acts as an explanatory and narrative summarization layer on top of the verified metrics."
    )
    pdf.multi_cell(0, 5, text)
    pdf.ln(5)
    
    # 1.1 Weighted Signals Header
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "1.1 Weighted Signals Model", ln=1)
    pdf.ln(2)
    
    # Table Header
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(18, 43, 64)
    pdf.cell(40, 7, "Signal Layer", border=1, fill=True)
    pdf.cell(20, 7, "Weight", border=1, fill=True, align="C")
    pdf.cell(130, 7, "Computation & Normalization Logic", border=1, fill=True)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(60, 60, 60)
    
    rows = [
        ("Schedule Slippage", "30%", "Scans schedule health column for explicit 'Red'/'Amber' flags; checks total float erosion and counts late active tasks."),
        ("Progress Gap", "20%", "Compares actual percent complete against the expected progress linearly calculated from elapsed timeline."),
        ("Milestone Health", "20%", "Analyzes incomplete key milestones, measuring the ratio of delayed/high-risk milestones to completed ones."),
        ("Blockers & Float", "15%", "Identifies critical path tasks, negative total float, and checks task comments/predecessors for blocker keywords."),
        ("Sentiment Theme", "10%", "Evaluates the emotional tone, outlook, and thematic urgency of PM comments on a scale from 0 to 100."),
        ("Budget Burn", "5%", "Calculates cost variance and burn rates. Excluded if budget data is missing (weights re-normalize to remaining 95%).")
    ]
    
    for r_title, r_weight, r_desc in rows:
        pdf.cell(40, 7, r_title, border=1)
        pdf.cell(20, 7, r_weight, border=1, align="C")
        pdf.cell(130, 7, r_desc, border=1)
        pdf.ln()
        
    pdf.ln(5)
    
    # 1.2 Normalization & Status Mapping
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "1.2 Scoring Normalization & Mapping", ln=1)
    pdf.ln(2)
    
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 5, 
        "Overall project health is a weighted sum divided by total active weights. If budget data is absent, "
        "its weight is set to 0, and the remaining weights are normalized to sum to 1.0. "
        "The project score is mapped to the final RAG status as follows:\n"
        " - Green (Healthy): Score 0 to 34 and no critical override triggered.\n"
        " - Amber (Watch-list): Score 35 to 69.\n"
        " - Red (High-risk): Score 70 to 100, or if a critical override is active."
    )
    pdf.ln(5)
    
    # 1.3 Overrides
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "1.3 Critical Override Rules", ln=1)
    pdf.ln(2)
    pdf.multi_cell(0, 5,
        "To capture severe systemic risks that a weighted average might dilute, the engine applies overrides to force Red:\n"
        " 1. Severe Critical Path Delay: An incomplete critical path task delayed by > 15 working days.\n"
        " 2. Milestone Failure: A key milestone missing its baseline finish date by > 30 days and remaining incomplete.\n"
        " 3. Multiple Blockers: More than 3 active tasks flag-marked as blocked by external dependencies.\n"
        " 4. Widespread Red Schedule: Over 40% of active tasks flagged as 'Red' or 'Yellow' schedule health."
    )
    
    # Page 2
    pdf.add_page()
    pdf.set_y(25)
    
    # 2. Technical Stack
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "2. Technical Stack", ln=1)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Backend API & Processing Layer:", ln=1)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5,
        "- Python 3.10+: Static type annotations and strict coding patterns.\n"
        "- FastAPI & Uvicorn: High-performance asynchronous REST API backend (configured on port 8001).\n"
        "- SQLite Database: Re-writes, stores and queries snapshots, normalized tasks, comments, and RAG logs.\n"
        "- openpyxl: Robust Excel reader with safety checks and explicit file closures preventing Windows file locks.\n"
        "- python-pptx: Slide generator compiling widescreen monthly portfolio decks.\n"
        "- LLM API (Groq/Gemini): Processes structured JSON schemas for narratives, sentiment summaries, and themes."
    )
    pdf.ln(4)
    
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Frontend Dashboard Client:", ln=1)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5,
        "- React 19 & TypeScript: Modern single-page application framework.\n"
        "- Vite: Instant compilation and hot module reloading (dev server on port 3000).\n"
        "- TanStack Router: Declarative type-safe routing.\n"
        "- Tailwind CSS & Shadcn UI: Polished slate-themed responsive interface layouts.\n"
        "- TanStack Query: Optimized server-state caching and asynchronous query orchestration."
    )
    pdf.ln(6)

    # 3. Product Features
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "3. Product Features", ln=1)
    pdf.ln(2)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5,
        "- Resilient Ingestion: Hierarchy mapping using 'Level' or 'Ancestors' indentation trees.\n"
        "- Project Stage Fallback: Scans task nodes to find the current active phase if omitted in the summary.\n"
        "- Explainability Core: Renders details under 'Why this status' and 'Signals' citing row numbers.\n"
        "- Full Preservation: Renders every original workbook column raw attribute under 'Preserved attributes'.\n"
        "- Switcher & Deletion: Header project selector and cascade deletion of snapshot records and output files."
    )
    pdf.ln(6)

    # 4. End-to-End Lifecycle
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "4. Data Lifecycle", ln=1)
    pdf.ln(2)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5,
        "1. UPLOAD: React dropzone sends .xlsx workbook to backend.\n"
        "2. NORMALIZE: Python maps column schemas, filters empty rows, and detect stages.\n"
        "3. SCORE: Deterministic formulas evaluate metrics, and overrides are checked.\n"
        "4. AI SUMMARY: Groq/Llama-3.3 summarizes narratives and sentiments.\n"
        "5. PERSIST: Records are written to SQLite, and JSON/Markdown logs are stored.\n"
        "6. PRESENT: UI loads data in tables/tabs, and allows PowerPoint generation."
    )
    
    pdf.output(str(output_path))
    print(f"Generated: {output_path}")

def create_requirements_pdf(output_path: Path):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.set_y(25)
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 12, "Requirements & Deliverables Verification", ln=1)
    
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, "Supporting Submission Document for the Zycus AI Engineer Assignment", ln=1)
    pdf.ln(5)
    
    # Horizontal line
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    # Section 1: Requirements Matrix
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "1. Requirements Fulfilled", ln=1)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(240, 244, 248)
    pdf.set_text_color(18, 43, 64)
    pdf.cell(45, 7, "Assignment Requirement", border=1, fill=True)
    pdf.cell(20, 7, "Status", border=1, fill=True, align="C")
    pdf.cell(125, 7, "Implementation & Verification Detail", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(60, 60, 60)
    
    reqs = [
        ("Read Project Plan (.xlsx)", "Complete", "Excel reader parses multiple sheets. Normalizes task names, categories, dates, and hierarchies."),
        ("Preserve original values", "Complete", "Saves raw row dictionary data as JSON string in 'raw_data_json' column in SQLite tasks table."),
        ("Derive RAG status", "Complete", "Scored using 6 signal categories and overrides. Compares derived RAG against PM's schedule health."),
        ("Weekly output generation", "Complete", "Generates MD/JSON outputs in outputs/weekly/ for each parsed file with evidence details."),
        ("Store snapshots in SQL", "Complete", "Maintains historical runs in SQLite. Supports project lists, comments, quality audits, and tasks."),
        ("Synthesize monthly report", "Complete", "Executes monthly portfolio slide synthesis into exactly 6 widescreen slides using python-pptx."),
        ("QA & Normalization", "Complete", "Identifies incomplete data issues (severity/warning/info) and normalizes active stages using tree traversal."),
        ("Explainability & NLP", "Complete", "Integrates Groq Llama 3.3 for structured sentiment narratives. Cites specific row numbers for transparency.")
    ]
    
    for r_req, r_stat, r_det in reqs:
        pdf.cell(45, 7, r_req, border=1)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(20, 7, r_stat, border=1, align="C")
        pdf.set_text_color(60, 60, 60)
        pdf.cell(125, 7, r_det, border=1)
        pdf.ln()
        
    pdf.ln(5)
    
    # Section 2: Deliverables Location Matrix
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "2. Deliverables Location Guide", ln=1)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(240, 244, 248)
    pdf.set_text_color(18, 43, 64)
    pdf.cell(50, 7, "Deliverable Item", border=1, fill=True)
    pdf.cell(85, 7, "Workspace File / Directory Path", border=1, fill=True)
    pdf.cell(55, 7, "Purpose / Description", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(60, 60, 60)
    
    dels = [
        ("One-Page Methodology", "docs/rag_methodology.md / .pdf", "Formal scoring model, signal weights, overrides, and tech stack details."),
        ("Working AI Agent Core", "src/project_health/", "Clean Python module containing parser, scoring engine, API, and synthesizing CLI."),
        ("Interactive Dashboard UI", "frontend/", "React/Vite dashboard client (Vite Port 3000, proxies to API Port 8001)."),
        ("SQLite Database File", "storage/project_health.sqlite", "Fully seeded database containing analysis snapshots, task structures, and signals."),
        ("Sample Weekly Reports", "outputs/weekly/*.[md/json]", "Weekly outputs demonstrating RAG calculations on the Green, Amber, Red plans."),
        ("Final Executive Presentation", "outputs/monthly/monthly_project_health.pptx", "Widescreen 16:9 executive presentation deck comprising exactly 6 slides."),
        ("Setup & Instructions", "README.md", "Complete guides to install virtual environment dependencies and launch servers.")
    ]
    
    for d_item, d_path, d_desc in dels:
        pdf.cell(50, 7, d_item, border=1)
        pdf.cell(85, 7, d_path, border=1)
        pdf.cell(55, 7, d_desc, border=1)
        pdf.ln()
        
    pdf.ln(6)
    
    # Technical Note
    pdf.set_text_color(18, 43, 64)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Verification Instructions:", ln=1)
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5.5,
        "1. Backend validation: Run 'python -m pytest' in the root directory. All tests compile and pass.\n"
        "2. Server launch: Execute 'python run_api.py' to run FastAPI backend, and run 'npm run dev' inside frontend folder to launch client.\n"
        "3. Live manual testing: Navigate to http://localhost:3000 to upload plans, track, switch projects, and download the synthetic widescreen PPTX."
    )
    
    pdf.output(str(output_path))
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    create_methodology_pdf(docs_dir / "rag_methodology.pdf")
    create_requirements_pdf(docs_dir / "requirements_and_deliverables.pdf")
