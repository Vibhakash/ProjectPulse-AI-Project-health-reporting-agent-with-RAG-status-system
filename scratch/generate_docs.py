import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Colors
COLOR_SLATE_BLUE = RGBColor(18, 43, 64)      # #122B40
COLOR_DARK_SLATE = RGBColor(60, 60, 60)      # #3C3C3C
COLOR_MEDIUM_SLATE = RGBColor(100, 100, 100) # #646464
HEX_HEADER_BG = "F0F4F8"                     # Light Slate Blue Fill
HEX_SLATE_BLUE = "122B40"                    # Deep Slate Blue Fill

def set_cell_background(cell, fill_hex):
    """Applies XML background shading to a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def add_styled_paragraph(doc, text="", style='Normal', space_before=0, space_after=6, line_spacing=1.15):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_DARK_SLATE
    return p

def add_styled_heading(doc, text, level, space_before=12, space_after=6):
    h = doc.add_heading(level=level)
    h.paragraph_format.space_before = Pt(space_before)
    h.paragraph_format.space_after = Pt(space_after)
    h.paragraph_format.keep_with_next = True
    
    run = h.add_run(text)
    run.font.name = 'Arial'
    run.font.bold = True
    
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = COLOR_SLATE_BLUE
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_SLATE_BLUE
    else:
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_DARK_SLATE
    return h

def create_methodology_docx(output_path: Path):
    doc = Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    
    # Header Banner (using paragraph spacing and background color is hard in docx, so we use structured headings)
    p_header = doc.add_paragraph()
    p_header.paragraph_format.space_after = Pt(12)
    run_hdr = p_header.add_run("PROJECTPULSE AI - SYSTEM DOCUMENTATION")
    run_hdr.font.name = 'Arial'
    run_hdr.font.bold = True
    run_hdr.font.size = Pt(8.5)
    run_hdr.font.color.rgb = COLOR_MEDIUM_SLATE
    
    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("System Methodology & Technical Architecture")
    run_title.font.name = 'Arial'
    run_title.font.bold = True
    run_title.font.size = Pt(20)
    run_title.font.color.rgb = COLOR_SLATE_BLUE
    
    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("Deterministic RAG Scoring Engine, Natural Language Synthesis & System Architecture")
    run_sub.font.name = 'Arial'
    run_sub.font.italic = True
    run_sub.font.size = Pt(10)
    run_sub.font.color.rgb = COLOR_MEDIUM_SLATE
    
    # 1. RAG Determination Methodology
    add_styled_heading(doc, "1. RAG Determination Methodology", level=1)
    
    text = (
        "The core philosophy of the system is deterministic, auditable scoring. Instead of delegating "
        "RAG classification to black-box LLMs - which are susceptible to hallucination, inconsistency, "
        "and lack mathematical validation - the RAG classification is computed via a structured rule engine. "
        "The LLM acts as an explanatory and narrative summarization layer on top of the verified metrics."
    )
    p_desc = add_styled_paragraph(doc, text)
    
    # 1.1 Weighted Signals
    add_styled_heading(doc, "1.1 Weighted Signals Model", level=2)
    
    # Table Setup
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # Header cells
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Signal Layer'
    hdr_cells[1].text = 'Weight'
    hdr_cells[2].text = 'Computation & Normalization Logic'
    
    for i, cell in enumerate(hdr_cells):
        set_cell_background(cell, HEX_SLATE_BLUE)
        for p in cell.paragraphs:
            p.paragraph_format.space_after = Pt(2)
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
                
    # Data Rows
    rows = [
        ("Schedule Slippage", "30%", "Scans schedule health column for explicit 'Red'/'Amber' flags; checks total float erosion and counts late active tasks."),
        ("Progress Gap", "20%", "Compares actual percent complete against the expected progress linearly calculated from elapsed timeline."),
        ("Milestone Health", "20%", "Analyzes incomplete key milestones, measuring the ratio of delayed/high-risk milestones to completed ones."),
        ("Blockers & Float", "15%", "Identifies critical path tasks, negative total float, and checks task comments/predecessors for blocker keywords."),
        ("Sentiment Theme", "10%", "Evaluates the emotional tone, outlook, and thematic urgency of PM comments on a scale from 0 to 100."),
        ("Budget Burn", "5%", "Calculates cost variance and burn rates. Excluded if budget data is missing (weights re-normalize to remaining 95%).")
    ]
    
    for r_title, r_weight, r_desc in rows:
        row_cells = table.add_row().cells
        row_cells[0].text = r_title
        row_cells[1].text = r_weight
        row_cells[2].text = r_desc
        
        # Style row text
        for i, cell in enumerate(row_cells):
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Arial'
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = COLOR_DARK_SLATE
                    if i == 1:
                        # Center align weights
                        p.alignment = 1 # Center
                        
    # Table spacing
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(8)
    p_space.paragraph_format.space_after = Pt(2)
    
    # 1.2 Normalization & Status Mapping
    add_styled_heading(doc, "1.2 Scoring Normalization & Mapping", level=2)
    p_norm = add_styled_paragraph(doc, 
        "Overall project health is a weighted sum divided by total active weights. If budget data is absent, "
        "its weight is set to 0, and the remaining weights are normalized to sum to 1.0. "
        "The project score is mapped to the final RAG status as follows:"
    )
    p_g = doc.add_paragraph(style='List Bullet')
    p_g.paragraph_format.space_after = Pt(2)
    p_g.add_run("Green (Healthy): ").font.bold = True
    p_g.runs[0].font.name = 'Arial'
    p_g.runs[0].font.size = Pt(10)
    p_g.add_run("Score 0 to 34 and no critical override triggered.")
    p_g.runs[1].font.name = 'Arial'
    p_g.runs[1].font.size = Pt(10)
    
    p_a = doc.add_paragraph(style='List Bullet')
    p_a.paragraph_format.space_after = Pt(2)
    p_a.add_run("Amber (Watch-list): ").font.bold = True
    p_a.runs[0].font.name = 'Arial'
    p_a.runs[0].font.size = Pt(10)
    p_a.add_run("Score 35 to 69.")
    p_a.runs[1].font.name = 'Arial'
    p_a.runs[1].font.size = Pt(10)
    
    p_r = doc.add_paragraph(style='List Bullet')
    p_r.paragraph_format.space_after = Pt(6)
    p_r.add_run("Red (High-risk): ").font.bold = True
    p_r.runs[0].font.name = 'Arial'
    p_r.runs[0].font.size = Pt(10)
    p_r.add_run("Score 70 to 100, or if a critical override is active.")
    p_r.runs[1].font.name = 'Arial'
    p_r.runs[1].font.size = Pt(10)
    
    # 1.3 Critical Override Rules
    add_styled_heading(doc, "1.3 Critical Override Rules", level=2)
    add_styled_paragraph(doc, "To capture severe systemic risks that a weighted average might dilute, the engine applies overrides to force Red:")
    
    overrides = [
        "Severe Critical Path Delay: An incomplete critical path task delayed by > 15 working days.",
        "Milestone Failure: Key milestones missing baseline finish dates by > 30 days and remaining incomplete.",
        "Multiple Blockers: More than 3 active tasks flag-marked as blocked by external dependencies.",
        "Widespread Red Schedule: Over 40% of active tasks flagged as 'Red' or 'Yellow' schedule health."
    ]
    for idx, ovr in enumerate(overrides, 1):
        p_ovr = doc.add_paragraph()
        p_ovr.paragraph_format.left_indent = Inches(0.25)
        p_ovr.paragraph_format.space_after = Pt(3)
        run_num = p_ovr.add_run(f"{idx}. ")
        run_num.font.bold = True
        run_num.font.name = 'Arial'
        run_num.font.size = Pt(10)
        run_text = p_ovr.add_run(ovr)
        run_text.font.name = 'Arial'
        run_text.font.size = Pt(10)
        run_text.font.color.rgb = COLOR_DARK_SLATE

    # Page Break
    doc.add_page_break()
    
    # 2. Technical Stack
    add_styled_heading(doc, "2. Technical Stack", level=1)
    
    # Backend list
    add_styled_heading(doc, "Backend API & Processing Layer:", level=3, space_before=6)
    backend_bullets = [
        "Python 3.10+: Static type annotations and strict coding patterns.",
        "FastAPI & Uvicorn: High-performance asynchronous REST API backend (configured on port 8001).",
        "SQLite Database: Re-writes, stores and queries snapshots, normalized tasks, comments, and RAG logs.",
        "openpyxl: Robust Excel reader with safety checks and explicit file closures preventing Windows file locks.",
        "python-pptx: Slide generator compiling widescreen monthly portfolio decks.",
        "LLM API (Groq/Gemini): Processes structured JSON schemas for narratives, sentiment summaries, and themes."
    ]
    for b in backend_bullets:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(2)
        run_b = p_b.add_run(b)
        run_b.font.name = 'Arial'
        run_b.font.size = Pt(10)
        
    # Frontend list
    add_styled_heading(doc, "Frontend Dashboard Client:", level=3, space_before=8)
    frontend_bullets = [
        "React 19 & TypeScript: Modern single-page application framework.",
        "Vite: Instant compilation and hot module reloading (dev server on port 3000).",
        "TanStack Router: Declarative type-safe routing.",
        "Tailwind CSS & Shadcn UI: Polished slate-themed responsive interface layouts.",
        "TanStack Query: Optimized server-state caching and asynchronous query orchestration."
    ]
    for f in frontend_bullets:
        p_f = doc.add_paragraph(style='List Bullet')
        p_f.paragraph_format.space_after = Pt(2)
        run_f = p_f.add_run(f)
        run_f.font.name = 'Arial'
        run_f.font.size = Pt(10)
        
    doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # 3. Product Features
    add_styled_heading(doc, "3. Product Features", level=1)
    features = [
        "Resilient Ingestion: Hierarchy mapping using 'Level' or 'Ancestors' indentation trees.",
        "Project Stage Fallback: Scans task nodes to find the current active phase if omitted in the summary.",
        "Explainability Core: Renders details under 'Why this status' and 'Signals' citing row numbers.",
        "Full Preservation: Renders every original workbook column raw attribute under 'Preserved attributes'.",
        "Switcher & Deletion: Header project selector and cascade deletion of snapshot records and output files."
    ]
    for ft in features:
        p_ft = doc.add_paragraph(style='List Bullet')
        p_ft.paragraph_format.space_after = Pt(2)
        run_ft = p_ft.add_run(ft)
        run_ft.font.name = 'Arial'
        run_ft.font.size = Pt(10)
        
    doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # 4. Data Lifecycle
    add_styled_heading(doc, "4. Data Lifecycle", level=1)
    steps = [
        "UPLOAD: React dropzone sends .xlsx workbook to backend.",
        "NORMALIZE: Python maps column schemas, filters empty rows, and detects stages.",
        "SCORE: Deterministic formulas evaluate metrics, and overrides are checked.",
        "AI SUMMARY: Groq/Llama-3.3 summarizes narratives and sentiments.",
        "PERSIST: Records are written to SQLite, and JSON/Markdown logs are stored.",
        "PRESENT: UI loads data in tables/tabs, and allows PowerPoint generation."
    ]
    for idx, st in enumerate(steps, 1):
        p_st = doc.add_paragraph()
        p_st.paragraph_format.left_indent = Inches(0.25)
        p_st.paragraph_format.space_after = Pt(3)
        run_idx = p_st.add_run(f"{idx}. ")
        run_idx.font.bold = True
        run_idx.font.name = 'Arial'
        run_idx.font.size = Pt(10)
        run_text = p_st.add_run(st)
        run_text.font.name = 'Arial'
        run_text.font.size = Pt(10)
        
    doc.save(str(output_path))
    print(f"Generated docx: {output_path}")

def create_requirements_docx(output_path: Path):
    doc = Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    
    p_header = doc.add_paragraph()
    p_header.paragraph_format.space_after = Pt(12)
    run_hdr = p_header.add_run("PROJECTPULSE AI - SYSTEM DOCUMENTATION")
    run_hdr.font.name = 'Arial'
    run_hdr.font.bold = True
    run_hdr.font.size = Pt(8.5)
    run_hdr.font.color.rgb = COLOR_MEDIUM_SLATE
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("Requirements & Deliverables Verification")
    run_title.font.name = 'Arial'
    run_title.font.bold = True
    run_title.font.size = Pt(20)
    run_title.font.color.rgb = COLOR_SLATE_BLUE
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("Supporting Submission Document for the Zycus AI Engineer Assignment")
    run_sub.font.name = 'Arial'
    run_sub.font.italic = True
    run_sub.font.size = Pt(10)
    run_sub.font.color.rgb = COLOR_MEDIUM_SLATE
    
    # Section 1
    add_styled_heading(doc, "1. Requirements Fulfilled", level=1)
    
    table1 = doc.add_table(rows=1, cols=3)
    table1.style = 'Table Grid'
    
    hdr1 = table1.rows[0].cells
    hdr1[0].text = 'Assignment Requirement'
    hdr1[1].text = 'Status'
    hdr1[2].text = 'Implementation & Verification Detail'
    
    for cell in hdr1:
        set_cell_background(cell, HEX_SLATE_BLUE)
        for p in cell.paragraphs:
            p.paragraph_format.space_after = Pt(2)
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
                
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
        row_cells = table1.add_row().cells
        row_cells[0].text = r_req
        row_cells[1].text = r_stat
        row_cells[2].text = r_det
        
        for i, cell in enumerate(row_cells):
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Arial'
                    run.font.size = Pt(8.5)
                    if i == 1:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0, 100, 0) # Green text
                        p.alignment = 1 # Center
                    else:
                        run.font.color.rgb = COLOR_DARK_SLATE
                        
    # Spacer
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    
    # Section 2
    add_styled_heading(doc, "2. Deliverables Location Guide", level=1)
    
    table2 = doc.add_table(rows=1, cols=3)
    table2.style = 'Table Grid'
    
    hdr2 = table2.rows[0].cells
    hdr2[0].text = 'Deliverable Item'
    hdr2[1].text = 'Workspace File / Directory Path'
    hdr2[2].text = 'Purpose / Description'
    
    for cell in hdr2:
        set_cell_background(cell, HEX_SLATE_BLUE)
        for p in cell.paragraphs:
            p.paragraph_format.space_after = Pt(2)
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
                
    dels = [
        ("One-Page Methodology", "docs/rag_methodology.md / .pdf / .docx", "Formal scoring model, signal weights, overrides, and tech stack details."),
        ("Working AI Agent Core", "src/project_health/", "Clean Python module containing parser, scoring engine, API, and synthesizing CLI."),
        ("Interactive Dashboard UI", "frontend/", "React/Vite dashboard client (Vite Port 3000, proxies to API Port 8001)."),
        ("SQLite Database File", "storage/project_health.sqlite", "Fully seeded database containing analysis snapshots, task structures, and signals."),
        ("Sample Weekly Reports", "outputs/weekly/*.[md/json/docx]", "Weekly outputs demonstrating RAG calculations on the Green, Amber, Red plans."),
        ("Final Executive Presentation", "outputs/monthly/monthly_project_health.pptx", "Widescreen 16:9 executive presentation deck comprising exactly 6 slides."),
        ("Setup & Instructions", "README.md", "Complete guides to install virtual environment dependencies and launch servers.")
    ]
    
    for d_item, d_path, d_desc in dels:
        row_cells = table2.add_row().cells
        row_cells[0].text = d_item
        row_cells[1].text = d_path
        row_cells[2].text = d_desc
        
        for i, cell in enumerate(row_cells):
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Arial'
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = COLOR_DARK_SLATE
                    
    # Spacer
    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    
    # Section 3
    add_styled_heading(doc, "3. Verification Instructions", level=1)
    
    verifications = [
        "Backend validation: Run 'python -m pytest' in the root directory. All tests compile and pass.",
        "Server launch: Execute 'python run_api.py' to run FastAPI backend, and run 'npm run dev' inside frontend folder to launch client.",
        "Live manual testing: Navigate to http://localhost:3000 to upload plans, track, switch projects, and download the synthetic widescreen PPTX."
    ]
    
    for idx, ver in enumerate(verifications, 1):
        p_ver = doc.add_paragraph()
        p_ver.paragraph_format.left_indent = Inches(0.25)
        p_ver.paragraph_format.space_after = Pt(3)
        run_num = p_ver.add_run(f"{idx}. ")
        run_num.font.bold = True
        run_num.font.name = 'Arial'
        run_num.font.size = Pt(10)
        run_text = p_ver.add_run(ver)
        run_text.font.name = 'Arial'
        run_text.font.size = Pt(10)
        run_text.font.color.rgb = COLOR_DARK_SLATE
        
    doc.save(str(output_path))
    print(f"Generated docx: {output_path}")

if __name__ == "__main__":
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    create_methodology_docx(docs_dir / "rag_methodology.docx")
    create_requirements_docx(docs_dir / "requirements_and_deliverables.docx")
