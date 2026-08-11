"""
ProjectPulseAI — Test Data Generator
=====================================
Creates ready-to-upload test files that exercise every platform feature:

  test_files/
    Project_Alpha_Week1.xlsx   → Green status (2 weeks ago, Gantt dates, 5 tasks)
    Project_Alpha_Week2.xlsx   → Amber status (1 week ago, Gantt dates)
    Project_Alpha_Week3.xlsx   → Red status  (today, French comment for multi-language test)
    Project_Beta.xlsx          → Second distinct project (Green, for portfolio view)
  Test_Suite.zip               → All 4 files bundled for ZIP bulk-upload test

Features exercised
------------------
  ✔ Single file upload    → any file from test_files/
  ✔ ZIP bulk upload       → Test_Suite.zip (4 files)
  ✔ Trend chart           → Week1/2/3 of Project Alpha = 3 history points
  ✔ Gantt chart           → All tasks have valid Start/End/Baseline dates
  ✔ Multi-language        → Week3 French comments
  ✔ Comments section      → All files have status comments
  ✔ PDF export            → Works on any snapshot
  ✔ Portfolio dashboard   → Multiple projects visible
"""

import os
import zipfile
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# ── Styling helpers ───────────────────────────────────────────────────────────
INDIGO   = "4F46E5"
WHITE    = "FFFFFF"
ALT_ROW  = "EEF2FF"
RED_ROW  = "FEF2F2"
AMBER_ROW= "FFFBEB"

def _hfont(bold=True, color=WHITE):  return Font(bold=bold, color=color)
def _fill(hex_):                     return PatternFill("solid", fgColor=hex_)
def _border():
    s = Side(style="thin", color="CBD5E1")
    return Border(left=s, right=s, top=s, bottom=s)

HEADERS = [
    "Task Name", "Status", "% Complete",
    "Start Date", "End Date",
    "Baseline Start", "Baseline Finish",
    "Total Float", "Critical",
    "Schedule Health", "Owner", "Comments", "Phase / Milestone",
]

def make_xlsx(path: str, tasks: list[list], project_display_name: str = "") -> str:
    """
    Write an xlsx file that the ProjectPulseAI normalizer can read.
    Headers go on row 1; task data starts on row 2.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Project Plan"

    # ── Row 1: headers ────────────────────────────────────────────────────────
    for col, h in enumerate(HEADERS, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font   = _hfont()
        c.fill   = _fill(INDIGO)
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = _border()
    ws.row_dimensions[1].height = 20

    # ── Rows 2+: task data ────────────────────────────────────────────────────
    health_fill_map = {"Green": "F0FFF4", "Amber": AMBER_ROW, "Red": RED_ROW}
    for ridx, row in enumerate(tasks, 2):
        health = str(row[9]) if len(row) > 9 else "Green"
        row_fill = _fill(health_fill_map.get(health, ALT_ROW) if ridx % 2 == 0 else "FFFFFF")
        for cidx, val in enumerate(row, 1):
            c = ws.cell(row=ridx, column=cidx, value=val)
            c.fill   = row_fill
            c.border = _border()
            c.alignment = Alignment(vertical="center")

    # ── Column widths ─────────────────────────────────────────────────────────
    col_widths = [38, 14, 12, 12, 12, 12, 15, 10, 8, 14, 12, 50, 16]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

    ws.freeze_panes = "A2"  # Freeze header row

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    wb.save(path)
    print(f"  OK  {path}")
    return path

# ── Date helpers ──────────────────────────────────────────────────────────────
today = datetime.now()
def d(delta_days: int) -> str:
    return (today + timedelta(days=delta_days)).strftime("%Y-%m-%d")


def generate():
    os.makedirs("test_files", exist_ok=True)
    files = []

    # ── Project Alpha · Week 1 · Green ───────────────────────────────────────
    # Project name comes from the first root-level task name
    w1 = [
        # Task Name                              Status       %    Start    End      BL Start  BL End   Float  Crit   Health   Owner    Comment                              Phase
        ["Platform Migration Project",           "In Progress",45, d(-60),  d(60),   d(-60),   d(60),   12,    False, "Green", "Alice", "Project on track. All milestones met so far.", None],
        ["1.1  Requirements & Scoping",          "Completed",  100,d(-60),  d(-40),  d(-60),   d(-40),  8,     False, "Green", "Alice", "Completed two days ahead of schedule.",          None],
        ["1.2  Architecture Design",             "Completed",  100,d(-39),  d(-20),  d(-39),   d(-20),  6,     False, "Green", "Bob",   "Design approved by all stakeholders.",           None],
        ["1.3  Dev Environment Setup",           "In Progress",60, d(-19),  d(5),    d(-19),   d(5),    5,     False, "Green", "Carol", "Progressing. 60% done.",                         None],
        ["1.4  Core Module Development",         "Not Started",0,  d(6),    d(40),   d(6),     d(40),   8,     False, "Green", "Dave",  "Ready to start after environment sign-off.",     None],
        ["MILESTONE: Phase 1 Sign-off",          "Not Started",0,  d(5),    d(5),    d(5),     d(5),    0,     False, "Green", "Alice", "",                                               "Milestone"],
    ]
    files.append(make_xlsx("test_files/Project_Alpha_Week1.xlsx", w1))

    # ── Project Alpha · Week 2 · Amber ───────────────────────────────────────
    w2 = [
        ["Platform Migration Project",           "In Progress",52, d(-60),  d(75),   d(-60),   d(60),   -8,    True,  "Amber","Alice", "Project slipping. Vendor delayed Phase 2 kickoff by 2 weeks.",None],
        ["1.1  Requirements & Scoping",          "Completed",  100,d(-60),  d(-40),  d(-60),   d(-40),  8,     False, "Green","Alice", "Complete.",                                      None],
        ["1.2  Architecture Design",             "Completed",  100,d(-39),  d(-20),  d(-39),   d(-20),  6,     False, "Green","Bob",   "Complete.",                                      None],
        ["1.3  Dev Environment Setup",           "In Progress",80, d(-19),  d(12),   d(-19),   d(5),    -4,    True,  "Amber","Carol", "Vendor feedback delayed sign-off. Blocked on external dependency.",None],
        ["1.4  Core Module Development",         "Not Started",0,  d(13),   d(50),   d(6),     d(40),   -8,    True,  "Amber","Dave",  "Delayed due to environment setup overrun.",      None],
        ["MILESTONE: Phase 1 Sign-off",          "Delayed",    0,  d(12),   d(12),   d(5),     d(5),    -7,    True,  "Amber","Alice", "Missed original milestone date.",                "Milestone"],
    ]
    files.append(make_xlsx("test_files/Project_Alpha_Week2.xlsx", w2))

    # ── Project Alpha · Week 3 · Red (with French comments) ──────────────────
    w3 = [
        ["Platform Migration Project",           "In Progress",55, d(-60),  d(90),   d(-60),   d(60),   -22,   True,  "Red",  "Alice", "Le projet est sérieusement en danger. Les problèmes budgétaires et les retards du fournisseur mettent en péril les livrables clés. Une décision de direction est urgente.",None],
        ["1.1  Requirements & Scoping",          "Completed",  100,d(-60),  d(-40),  d(-60),   d(-40),  0,     False, "Green","Alice", "Terminé.",                                       None],
        ["1.2  Architecture Design",             "Completed",  100,d(-39),  d(-20),  d(-39),   d(-20),  0,     False, "Green","Bob",   "Complete.",                                      None],
        ["1.3  Dev Environment Setup",           "On Hold",    80, d(-19),  d(25),   d(-19),   d(5),    -18,   True,  "Red",  "Carol", "BLOCKED — vendor contract terminated unexpectedly. Cannot proceed without a replacement partner.",None],
        ["1.4  Core Module Development",         "Not Started",0,  d(25),   d(70),   d(6),     d(40),   -22,   True,  "Red",  "Dave",  "Cannot start. Predecessor is on hold. Risk of full programme delay.",None],
        ["1.5  Integration Testing",             "Not Started",0,  d(70),   d(100),  d(40),    d(70),   -30,   True,  "Red",  "Eve",   "Not scheduled. Critical path at risk of 30+ day slip.",None],
        ["MILESTONE: Phase 1 Sign-off",          "Missed",     0,  d(-5),   d(-5),   d(5),     d(5),    -30,   True,  "Red",  "Alice", "Milestone was missed. Requires board-level escalation.", "Milestone"],
    ]
    files.append(make_xlsx("test_files/Project_Alpha_Week3.xlsx", w3))

    # ── Project Beta · Single snapshot · Green (second project for portfolio) ─
    beta = [
        ["Cloud Security Compliance",            "In Progress",70, d(-90),  d(30),   d(-90),   d(30),   15,    False, "Green","Frank", "All compliance controls on track. Final audit in 4 weeks.",None],
        ["2.1  Risk Assessment",                 "Completed",  100,d(-90),  d(-60),  d(-90),   d(-60),  10,    False, "Green","Frank", "Risk register approved.",                         None],
        ["2.2  Policy Framework",                "Completed",  100,d(-59),  d(-30),  d(-59),   d(-30),  8,     False, "Green","Grace", "All 47 policies signed off.",                    None],
        ["2.3  Technical Controls Implementation","In Progress",65, d(-29),  d(10),   d(-29),   d(10),   6,     False, "Green","Hank",  "Controls deployment is 65% complete.",           None],
        ["2.4  External Audit Preparation",      "Not Started",0,  d(11),   d(30),   d(11),    d(30),   15,    False, "Green","Frank", "Audit pack in progress.",                        None],
        ["MILESTONE: ISO 27001 Audit",           "Not Started",0,  d(30),   d(30),   d(30),    d(30),   0,     False, "Green","Frank", "",                                               "Milestone"],
    ]
    files.append(make_xlsx("test_files/Project_Beta_CloudCompliance.xlsx", beta))

    # ── Create ZIP ────────────────────────────────────────────────────────────
    zip_path = "Test_Suite.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in files:
            zf.write(fp, os.path.basename(fp))
    print(f"\n  ZIP  {zip_path}  ({os.path.getsize(zip_path):,} bytes)\n")

    print("=" * 60)
    print("DONE. Files ready for upload:")
    print()
    print("  Single file tests:")
    print("    test_files/Project_Alpha_Week1.xlsx          - Green status")
    print("    test_files/Project_Alpha_Week2.xlsx          - Amber status")
    print("    test_files/Project_Alpha_Week3.xlsx          - Red + French comments")
    print("    test_files/Project_Beta_CloudCompliance.xlsx - Green project 2")
    print()
    print("  Bulk ZIP test (all 4 files):")
    print("    Test_Suite.zip")
    print()
    print("  Feature coverage:")
    print("    Trend chart     - Upload all 3 Alpha weeks; open any snapshot -> Trend tab")
    print("    Gantt chart     - All tasks have dates -> Gantt Chart tab")
    print("    Multi-language  - Week3 has French PM comments -> check AI Insights")
    print("    Comments tab    - All files have Comments column")
    print("    PDF export      - Snapshot detail page -> Export PDF button (top right)")
    print("    Portfolio view  - After ZIP upload: 4 projects in dashboard")
    print("=" * 60)


if __name__ == "__main__":
    generate()
