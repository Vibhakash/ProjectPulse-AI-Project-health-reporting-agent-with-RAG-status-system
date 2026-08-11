"""
Generate the official ProjectPulse AI project plan template (.xlsx).
Run with: python generate_template.py
"""
import os

try:
    from openpyxl import Workbook
    from openpyxl.styles import (
        PatternFill, Font, Alignment, Border, Side, GradientFill
    )
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    print("Installing openpyxl...")
    os.system(".venv\\Scripts\\pip install openpyxl")
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()

# ─── Color palette ────────────────────────────────────────────────────────────
C_HEADER_BG    = "1E3A5F"   # Dark navy header
C_HEADER_FG    = "FFFFFF"   # White text
C_REQUIRED_BG  = "EBF3FF"   # Light blue — required column
C_OPTIONAL_BG  = "F5F5F5"   # Light grey — optional column
C_TITLE_BG     = "2563EB"   # Blue — main title bar
C_SECTION_BG   = "DBEAFE"   # Pale blue — section title
C_RED          = "DC2626"
C_AMBER        = "D97706"
C_GREEN        = "16A34A"
C_BORDER       = "CBD5E1"

thin = Side(style="thin", color=C_BORDER)
thick_border = Border(left=thin, right=thin, top=thin, bottom=thin)

def hdr_fill(color):
    return PatternFill("solid", fgColor=color)

def hdr_font(bold=True, color="000000", size=10):
    return Font(bold=bold, color=color, name="Calibri", size=size)

def center_align(wrap=True):
    return Alignment(horizontal="center", vertical="center", wrap_text=wrap)

def left_align(wrap=True):
    return Alignment(horizontal="left", vertical="center", wrap_text=wrap)

# ─────────────────────────────────────────────────────────────────────────────
# SHEET 1: Project Plan Template
# ─────────────────────────────────────────────────────────────────────────────
ws = wb.active
ws.title = "Project Plan"
ws.sheet_view.showGridLines = False

# === Title bar ===
ws.merge_cells("A1:V1")
t = ws["A1"]
t.value = "📊  ProjectPulse AI — Official Project Plan Template"
t.fill = hdr_fill(C_TITLE_BG)
t.font = Font(bold=True, color="FFFFFF", name="Calibri", size=14)
t.alignment = center_align()
ws.row_dimensions[1].height = 30

ws.merge_cells("A2:V2")
sub = ws["A2"]
sub.value = "Fill in each row with one task or milestone. Columns marked ★ are REQUIRED for accurate RAG scoring. All date columns must be in DD-MMM-YYYY or YYYY-MM-DD format."
sub.fill = hdr_fill(C_SECTION_BG)
sub.font = Font(color="1E40AF", name="Calibri", size=9, italic=True)
sub.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws.row_dimensions[2].height = 28

# === Column definitions ===
columns = [
    # (Header label, width, required, example, description)
    ("ID",                         8,  True,  "1",               "Unique numeric ID per task row"),
    ("WBS",                        10, False, "1.1.2",           "Work Breakdown Structure code (e.g. 1.2.3)"),
    ("Task Name ★",                38, True,  "Design Review",   "Full task or milestone name"),
    ("Phase / Milestone",          22, False, "Phase 1: Design", "High-level phase or milestone grouping"),
    ("Ancestors",                  28, False, "Project > Phase1","Parent task chain (> separated)"),
    ("Level",                      8,  False, "2",               "Hierarchy depth (1=top, 2=sub, etc.)"),
    ("Status ★",                   16, True,  "In Progress",     "Not Started / In Progress / Completed / On Hold"),
    ("Schedule Health ★",          18, True,  "Amber",           "Red / Amber / Green — PM's own assessment"),
    ("% Complete ★",               14, True,  "45",              "Numeric 0-100 (no % sign needed)"),
    ("Start Date ★",               16, True,  "01-Jun-2025",     "Planned start date (DD-MMM-YYYY)"),
    ("End Date ★",                 16, True,  "30-Sep-2025",     "Planned end date (DD-MMM-YYYY)"),
    ("Baseline Start",             16, False, "01-Jun-2025",     "Original baseline start before changes"),
    ("Baseline Finish ★",          16, True,  "30-Sep-2025",     "Original baseline finish — used for variance"),
    ("Variance (days)",            16, False, "5",               "Positive = late, Negative = ahead"),
    ("Total Float (days) ★",       18, True,  "0",               "Scheduling float; 0 or negative = critical risk"),
    ("Critical ★",                 12, True,  "Yes",             "Yes / No — is this on the critical path?"),
    ("On Hold",                    12, False, "No",              "Yes / No — is this task currently blocked/paused?"),
    ("Owner",                      18, False, "Alice Smith",     "Responsible person / team"),
    ("Assigned To",                18, False, "Bob Jones",       "Individual assignee name"),
    ("Status Comment",             40, False, "Pending vendor approval for hardware delivery", "Free-text PM note about this task's health"),
    ("Predecessors",               18, False, "3,5",             "Comma-separated IDs of predecessor tasks"),
    ("Budget (USD)",               14, False, "15000",           "Planned budget for this task"),
]

# Header row (row 3)
for col_idx, (label, width, required, _, _desc) in enumerate(columns, start=1):
    cell = ws.cell(row=3, column=col_idx)
    cell.value = label
    cell.fill = hdr_fill(C_HEADER_BG)
    cell.font = hdr_font(color="FFFFFF", size=10)
    cell.alignment = center_align()
    cell.border = thick_border
    ws.column_dimensions[get_column_letter(col_idx)].width = width

ws.row_dimensions[3].height = 36

# Description row (row 4)
for col_idx, (_, _, required, example, desc) in enumerate(columns, start=1):
    cell = ws.cell(row=4, column=col_idx)
    cell.value = f"e.g. {example}\n{desc}"
    cell.fill = hdr_fill(C_REQUIRED_BG if required else C_OPTIONAL_BG)
    cell.font = Font(color="374151", name="Calibri", size=8, italic=True)
    cell.alignment = left_align()
    cell.border = thick_border

ws.row_dimensions[4].height = 42

# === Sample task data (rows 5-14) ===
sample_tasks = [
    [1, "1",   "PROJECT: E-Commerce Platform Relaunch", "Project",      "Project",                   1, "In Progress",  "Amber",  35, "01-Jan-2025", "31-Dec-2025", "01-Jan-2025", "31-Dec-2025", 0,   10,  "No",  "No",  "PMO",           "Jane Doe",    "Q3 milestone at risk due to vendor delays",      "",    ""],
    [2, "1.1", "Phase 1: Discovery & Requirements",     "Phase 1",      "PROJECT",                   2, "Completed",    "Green",  100,"01-Jan-2025", "28-Feb-2025", "01-Jan-2025", "28-Feb-2025", 0,   20,  "No",  "No",  "BA Team",       "Alice Smith", "",                                                "",    ""],
    [3, "1.2", "Stakeholder Workshops",                 "Phase 1",      "PROJECT > Phase 1",         3, "Completed",    "Green",  100,"01-Jan-2025", "15-Jan-2025", "01-Jan-2025", "15-Jan-2025", 0,   0,   "Yes", "No",  "Alice Smith",   "Alice Smith", "",                                                "1",   "3000"],
    [4, "1.3", "Requirements Sign-off",                 "Phase 1",      "PROJECT > Phase 1",         3, "Completed",    "Green",  100,"16-Jan-2025", "28-Feb-2025", "16-Jan-2025", "28-Feb-2025", 0,   5,   "No",  "No",  "Alice Smith",   "Client",      "",                                                "3",   "1000"],
    [5, "2",   "Phase 2: UI/UX Design",                 "Phase 2",      "PROJECT",                   2, "In Progress",  "Amber",  60, "01-Mar-2025", "30-May-2025", "01-Mar-2025", "30-Apr-2025", 30,  0,   "Yes", "No",  "Design Lead",   "Bob Jones",   "Delayed due to 2 rounds of client revisions",     "4",   "12000"],
    [6, "2.1", "Wireframes & Prototypes",               "Phase 2",      "PROJECT > Phase 2",         3, "Completed",    "Green",  100,"01-Mar-2025", "31-Mar-2025", "01-Mar-2025", "31-Mar-2025", 0,   10,  "No",  "No",  "Bob Jones",     "Bob Jones",   "",                                                "4",   "5000"],
    [7, "2.2", "High-Fidelity Mockups",                 "Phase 2",      "PROJECT > Phase 2",         3, "In Progress",  "Red",    40, "01-Apr-2025", "30-May-2025", "01-Apr-2025", "30-Apr-2025", 30,  0,   "Yes", "No",  "Bob Jones",     "Carol Lee",   "BLOCKED: Client feedback not received on time",   "6",   "7000"],
    [8, "3",   "Phase 3: Backend Development",          "Phase 3",      "PROJECT",                   2, "In Progress",  "Green",  55, "01-Apr-2025", "31-Jul-2025", "01-Apr-2025", "31-Jul-2025", 0,   8,   "Yes", "No",  "Dev Lead",      "Dev Team",    "",                                                "5",   "45000"],
    [9, "3.1", "API Gateway Setup",                     "Phase 3",      "PROJECT > Phase 3",         3, "Completed",    "Green",  100,"01-Apr-2025", "30-Apr-2025", "01-Apr-2025", "30-Apr-2025", 0,   12,  "No",  "No",  "Sam Patel",     "Sam Patel",   "",                                                "5",   "8000"],
    [10,"3.2", "Core Services Development",             "Phase 3",      "PROJECT > Phase 3",         3, "In Progress",  "Amber",  45, "01-May-2025", "31-Jul-2025", "01-May-2025", "30-Jun-2025", 31,  -2,  "Yes", "No",  "Sam Patel",     "Dev Team",    "Pending vendor API documentation delivery",       "9",   "22000"],
]

for row_idx, row_data in enumerate(sample_tasks, start=5):
    for col_idx, val in enumerate(row_data, start=1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.value = val
        is_required = columns[col_idx - 1][2]
        cell.fill = hdr_fill(C_REQUIRED_BG if is_required else C_OPTIONAL_BG)
        cell.font = Font(name="Calibri", size=9)
        cell.alignment = left_align()
        cell.border = thick_border
    ws.row_dimensions[row_idx].height = 22

# Add 40 blank editable rows
for row_idx in range(15, 55):
    for col_idx, (_, _, required, _, _) in enumerate(columns, start=1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.fill = hdr_fill("FAFAFA" if required else "F9FAFB")
        cell.font = Font(name="Calibri", size=9)
        cell.alignment = left_align()
        cell.border = thick_border
    ws.row_dimensions[row_idx].height = 20

# Data validation for Status
dv_status = DataValidation(
    type="list",
    formula1='"Not Started,In Progress,Completed,On Hold,Cancelled"',
    allow_blank=True,
    showDropDown=False,
)
dv_status.sqref = "G5:G54"
ws.add_data_validation(dv_status)

# Data validation for Schedule Health
dv_health = DataValidation(
    type="list",
    formula1='"Red,Amber,Green,Yellow"',
    allow_blank=True,
    showDropDown=False,
)
dv_health.sqref = "H5:H54"
ws.add_data_validation(dv_health)

# Data validation for Critical
dv_crit = DataValidation(
    type="list",
    formula1='"Yes,No"',
    allow_blank=True,
    showDropDown=False,
)
dv_crit.sqref = "P5:P54"
ws.add_data_validation(dv_crit)

# Data validation for On Hold
dv_hold = DataValidation(
    type="list",
    formula1='"Yes,No"',
    allow_blank=True,
    showDropDown=False,
)
dv_hold.sqref = "Q5:Q54"
ws.add_data_validation(dv_hold)

# Freeze header rows
ws.freeze_panes = "A5"

# ─────────────────────────────────────────────────────────────────────────────
# SHEET 2: Column Reference Guide
# ─────────────────────────────────────────────────────────────────────────────
ws2 = wb.create_sheet("Column Reference Guide")
ws2.sheet_view.showGridLines = False

ws2.merge_cells("A1:G1")
t2 = ws2["A1"]
t2.value = "ProjectPulse AI — Column Reference Guide"
t2.fill = hdr_fill(C_TITLE_BG)
t2.font = Font(bold=True, color="FFFFFF", name="Calibri", size=14)
t2.alignment = center_align()
ws2.row_dimensions[1].height = 30

ws2.merge_cells("A2:G2")
sub2 = ws2["A2"]
sub2.value = "This guide explains every column, whether it is required, which signal it feeds, and what values are accepted."
sub2.fill = hdr_fill(C_SECTION_BG)
sub2.font = Font(color="1E40AF", name="Calibri", size=9, italic=True)
sub2.alignment = center_align()
ws2.row_dimensions[2].height = 22

ref_headers = ["Column Name", "Required?", "Signal It Feeds", "Accepted Values", "Format", "Example", "Notes"]
ref_col_widths = [30, 12, 30, 38, 22, 28, 45]
for ci, (h, w) in enumerate(zip(ref_headers, ref_col_widths), start=1):
    cell = ws2.cell(row=3, column=ci)
    cell.value = h
    cell.fill = hdr_fill(C_HEADER_BG)
    cell.font = hdr_font(color="FFFFFF")
    cell.alignment = center_align()
    cell.border = thick_border
    ws2.column_dimensions[get_column_letter(ci)].width = w
ws2.row_dimensions[3].height = 30

ref_data = [
    ["Task Name",         "★ YES", "All signals",                  "Any text",                                            "Text",             "Design Review",             "Must be non-empty. Used as the primary task identifier."],
    ["Status",            "★ YES", "Schedule Slippage, Blockers",  "Not Started / In Progress / Completed / On Hold",     "Dropdown list",    "In Progress",               "Used to detect stalled or blocked tasks."],
    ["Schedule Health",   "★ YES", "Schedule Slippage (30%)",      "Red / Amber / Green / Yellow",                        "Text / Dropdown",  "Amber",                     "Core signal. PM's own assessment of schedule status."],
    ["% Complete",        "★ YES", "Progress Gap (20%)",           "0 to 100 (numeric, no % sign)",                       "Number",           "45",                        "Compared to expected linear progress based on timeline."],
    ["Start Date",        "★ YES", "Progress Gap, Schedule",       "Any date",                                            "DD-MMM-YYYY",      "01-Jun-2025",               "Used to calculate elapsed time and expected progress."],
    ["End Date",          "★ YES", "Progress Gap, Schedule",       "Any date",                                            "DD-MMM-YYYY",      "30-Sep-2025",               "Planned completion date."],
    ["Baseline Finish",   "★ YES", "Milestone Health (20%)",       "Any date",                                            "DD-MMM-YYYY",      "30-Sep-2025",               "Original committed finish. Used to detect milestone slippage."],
    ["Total Float",       "★ YES", "Blockers & Critical (15%)",    "Integer (negative means overdue)",                    "Number (days)",    "0",                         "Negative float flags critical path risk. Key override trigger."],
    ["Critical",          "★ YES", "Blockers & Critical (15%)",    "Yes / No",                                            "Dropdown",         "Yes",                       "Tasks on the critical path. Key override trigger."],
    ["Status Comment",    "Optional","Stakeholder Sentiment (10%)",  "Free text",                                           "Text",             "Pending vendor approval",   "PM notes. Scanned for blocker keywords and sentiment."],
    ["Phase / Milestone", "Optional","Milestone Health (20%)",       "Any text",                                            "Text",             "Phase 2: Design",           "Groups tasks into phases. Helps milestone health scoring."],
    ["Baseline Start",    "Optional","Milestone Health",             "Any date",                                            "DD-MMM-YYYY",      "01-Jun-2025",               "Used alongside Baseline Finish for variance calculation."],
    ["Variance (days)",   "Optional","Schedule Slippage",           "Integer",                                             "Number (days)",    "15",                        "Positive = late. Auto-calculated if not provided."],
    ["On Hold",           "Optional","Blockers",                    "Yes / No",                                            "Dropdown",         "No",                        "Flags paused/blocked tasks."],
    ["Owner",             "Optional","(Metadata only)",             "Name or team",                                        "Text",             "Alice Smith",               "For reporting display only. Not used in scoring."],
    ["Assigned To",       "Optional","(Metadata only)",             "Name",                                                "Text",             "Bob Jones",                 "For reporting display only. Not used in scoring."],
    ["Predecessors",      "Optional","Blockers",                    "Comma-separated task IDs",                            "e.g. 3,5",         "3,5",                       "Helps detect dependency chain blockers."],
    ["Budget (USD)",      "Optional","Budget Burn (5%)",            "Numeric amount",                                      "Number",           "15000",                     "If absent for any task, budget signal is excluded and weights are renormalized."],
    ["WBS",               "Optional","(Metadata only)",             "Dot-separated code",                                  "e.g. 1.2.3",       "1.2.3",                     "Work breakdown structure code for hierarchy."],
    ["Ancestors",         "Optional","(Hierarchy detection)",       "Parent names separated by >",                         "Text",             "Project > Phase 1",         "Alternative hierarchy indicator. Used if Level is not provided."],
    ["Level",             "Optional","(Hierarchy detection)",       "Integer (1=top level)",                               "Number",           "2",                         "Explicit depth in task tree. If missing, inferred from Ancestors."],
    ["ID",                "Optional","(Row tracking)",              "Any unique value",                                    "Number or text",   "1",                         "Used for predecessor references. Auto-assigned if missing."],
]

for ri, row in enumerate(ref_data, start=4):
    bg = C_REQUIRED_BG if row[1].startswith("★") else C_OPTIONAL_BG
    for ci, val in enumerate(row, start=1):
        cell = ws2.cell(row=ri, column=ci)
        cell.value = val
        cell.fill = hdr_fill(bg)
        cell.font = Font(name="Calibri", size=9)
        cell.alignment = left_align()
        cell.border = thick_border
    ws2.row_dimensions[ri].height = 28

ws2.freeze_panes = "A4"

# ─────────────────────────────────────────────────────────────────────────────
# SHEET 3: RAG Legend & Tips
# ─────────────────────────────────────────────────────────────────────────────
ws3 = wb.create_sheet("RAG Guide & Tips")
ws3.sheet_view.showGridLines = False

ws3.merge_cells("A1:D1")
t3 = ws3["A1"]
t3.value = "ProjectPulse AI — RAG Scoring Guide & Tips"
t3.fill = hdr_fill(C_TITLE_BG)
t3.font = Font(bold=True, color="FFFFFF", name="Calibri", size=14)
t3.alignment = center_align()
ws3.row_dimensions[1].height = 30

guide_data = [
    ("", ""),
    ("RAG STATUS THRESHOLDS", ""),
    ("Score Range", "Status & Meaning"),
    ("0 – 34",   "🟢 GREEN — Project is on track. No critical overrides triggered. Data quality sufficient."),
    ("35 – 69",  "🟡 AMBER — Watch-list. Minor delays, progress gaps, or warning signals detected."),
    ("70 – 100", "🔴 RED — Critical. Significant delays, blocked milestones, or override rules triggered."),
    ("", ""),
    ("CRITICAL OVERRIDE RULES (These force RED regardless of score)", ""),
    ("Rule 1", "A critical path task is delayed by more than 15 working days."),
    ("Rule 2", "A key milestone missed its baseline finish date by more than 30 days."),
    ("Rule 3", "More than 3 tasks flagged as Blocked or On Hold simultaneously."),
    ("Rule 4", "Over 40% of active tasks show Red or Yellow Schedule Health."),
    ("", ""),
    ("TIPS FOR BEST RESULTS", ""),
    ("Tip 1", "Always fill in Baseline Finish. Without it, milestone health scoring is skipped."),
    ("Tip 2", "Use the Schedule Health dropdown exactly: Red / Amber / Green. Typos are ignored."),
    ("Tip 3", "Status Comment is powerful — write meaningful PM notes (e.g. 'Pending vendor approval for hardware'). The AI reads these."),
    ("Tip 4", "Fill in Total Float for every task. Negative values are the strongest single indicator of schedule risk."),
    ("Tip 5", "Mark Critical = Yes for any task on the critical path, not just the last task in the chain."),
    ("Tip 6", "You can upload multiple project files at once. Each file becomes one snapshot in the portfolio."),
    ("Tip 7", "Re-uploading an updated plan creates a new snapshot — old snapshots are preserved for trend tracking."),
]

col_widths3 = [45, 90]
for ci, w in enumerate(col_widths3, start=1):
    ws3.column_dimensions[get_column_letter(ci)].width = w

for ri, (label, value) in enumerate(guide_data, start=2):
    if not label and not value:
        ws3.row_dimensions[ri].height = 12
        continue

    section_headers = ["RAG STATUS THRESHOLDS", "CRITICAL OVERRIDE RULES (These force RED regardless of score)", "TIPS FOR BEST RESULTS"]
    col_headers = [("Score Range", "Status & Meaning")]

    if label in section_headers:
        ws3.merge_cells(f"A{ri}:D{ri}")
        cell = ws3.cell(row=ri, column=1)
        cell.value = f"  {label}"
        cell.fill = hdr_fill("1E3A5F")
        cell.font = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
        cell.alignment = left_align(wrap=False)
        ws3.row_dimensions[ri].height = 24
    elif (label, value) in col_headers:
        for ci, v in enumerate([label, value], start=1):
            cell = ws3.cell(row=ri, column=ci)
            cell.value = v
            cell.fill = hdr_fill(C_HEADER_BG)
            cell.font = hdr_font(color="FFFFFF")
            cell.alignment = center_align()
            cell.border = thick_border
        ws3.row_dimensions[ri].height = 22
    else:
        bg = "F0FDF4" if "GREEN" in value else "FFFBEB" if "AMBER" in value else "FEF2F2" if "RED" in value else "F8FAFC"
        for ci, v in enumerate([label, value], start=1):
            cell = ws3.cell(row=ri, column=ci)
            cell.value = v
            cell.fill = hdr_fill(bg)
            cell.font = Font(name="Calibri", size=9)
            cell.alignment = left_align()
            cell.border = thick_border
        ws3.row_dimensions[ri].height = 20

out_path = "data/ProjectPulseAI_Project_Plan_Template.xlsx"
os.makedirs("data", exist_ok=True)
wb.save(out_path)
print(f"[OK] Template saved to {out_path}")
