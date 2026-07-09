"""
CLI utility to generate representative Excel workbooks for testing Project Health statuses.
Generates Green, Amber, and Red project plans in data/input/.
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

def create_workbook(
    file_path: Path,
    project_name: str,
    pm_name: str,
    rag_status: str,
    at_risk: str,
    project_stage: str,
    percent_complete: float,
    tasks_data: list[dict],
    comments_data: list[dict],
) -> None:
    wb = openpyxl.Workbook()
    
    # 1. Setup Summary Sheet
    ws_summary = wb.active
    ws_summary.title = "Summary"
    ws_summary.views.sheetView[0].showGridLines = True
    
    # Style definitions
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_body = Font(name="Segoe UI", size=10)
    font_title = Font(name="Segoe UI", size=14, bold=True)
    fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    ws_summary["A1"] = "Project Summary Dashboard"
    ws_summary["A1"].font = font_title
    
    summary_rows = [
        ("Project Name", project_name),
        ("Project Manager", pm_name),
        ("Project Start Date", date.today() - timedelta(days=60)),
        ("Project End Date", date.today() + timedelta(days=120)),
        ("Project Stage", project_stage),
        ("At Risk", at_risk),
        ("% Complete", percent_complete),
        ("Schedule Health", rag_status),
        ("Today's Date", date.today()),
        ("Duration", 180),
        ("Project Status", "In Progress"),
    ]
    
    for idx, (k, v) in enumerate(summary_rows, start=3):
        ws_summary.cell(row=idx, column=1, value=k).font = Font(name="Segoe UI", size=10, bold=True)
        ws_summary.cell(row=idx, column=2, value=v).font = font_body
        
    # 2. Setup Tasks Sheet
    ws_tasks = wb.create_sheet(title="Project Plan")
    ws_tasks.views.sheetView[0].showGridLines = True
    
    headers = [
        "Level", "Task Name", "Status", "% Complete", "Schedule Health",
        "Start Date", "End Date", "Baseline Start", "Baseline Finish",
        "Critical ?", "Total Float", "Comments", "Project Manager"
    ]
    
    for col_idx, header in enumerate(headers, start=1):
        cell = ws_tasks.cell(row=1, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center")
        
    for row_idx, t in enumerate(tasks_data, start=2):
        for col_idx, header in enumerate(headers, start=1):
            val = t.get(header)
            cell = ws_tasks.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_body
            if header in ("Start Date", "End Date", "Baseline Start", "Baseline Finish") and isinstance(val, date):
                cell.number_format = "yyyy-mm-dd"
            elif header == "% Complete" and isinstance(val, (int, float)):
                cell.number_format = "0.0%"
                
    # 3. Setup Comments Sheet
    ws_comments = wb.create_sheet(title="Comments")
    ws_comments.views.sheetView[0].showGridLines = True
    
    comment_headers = ["Reference Row", "Comment Text", "Author", "Created At"]
    for col_idx, h in enumerate(comment_headers, start=1):
        cell = ws_comments.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        
    for row_idx, c in enumerate(comments_data, start=2):
        ws_comments.cell(row=row_idx, column=1, value=c.get("row_ref")).font = font_body
        ws_comments.cell(row=row_idx, column=2, value=c.get("text")).font = font_body
        ws_comments.cell(row=row_idx, column=3, value=c.get("author")).font = font_body
        ws_comments.cell(row=row_idx, column=4, value=c.get("date")).font = font_body
        if isinstance(c.get("date"), date):
            ws_comments.cell(row=row_idx, column=4).number_format = "yyyy-mm-dd"

    # Auto-adjust column widths
    for ws in (ws_summary, ws_tasks, ws_comments):
        for col in ws.columns:
            max_len = 0
            for cell in col:
                val = cell.value
                if val is not None:
                    max_len = max(max_len, len(str(val)))
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 10)
            
    file_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(file_path)
    print(f"Generated test file: {file_path}")


def generate_all_test_plans() -> None:
    today = date.today()
    input_dir = Path("test_files")
    
    # ------------------ GREEN PLAN ------------------
    green_tasks = [
        # Root project
        {"Level": 0, "Task Name": "Zycus - Green Implementation Project", "Status": "In Progress", "% Complete": 0.60, "Schedule Health": "Green", "Start Date": today - timedelta(days=60), "End Date": today + timedelta(days=120), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today + timedelta(days=120), "Critical ?": "Yes", "Total Float": 10.0, "Comments": "On track, smooth progress", "Project Manager": "Jane Doe"},
        # Phase 1 - Completed
        {"Level": 1, "Task Name": "Design & Blueprint Phase", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Green", "Start Date": today - timedelta(days=60), "End Date": today - timedelta(days=30), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today - timedelta(days=30), "Critical ?": "No", "Total Float": 0.0, "Comments": "Completed on time", "Project Manager": "Jane Doe"},
        {"Level": 2, "Task Name": "Requirement Workshops", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Green", "Start Date": today - timedelta(days=60), "End Date": today - timedelta(days=45), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today - timedelta(days=45), "Critical ?": "No", "Total Float": 0.0, "Comments": "Sign-off obtained", "Project Manager": "Jane Doe"},
        {"Level": 2, "Task Name": "Design Document Sign-off", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Green", "Start Date": today - timedelta(days=45), "End Date": today - timedelta(days=30), "Baseline Start": today - timedelta(days=45), "Baseline Finish": today - timedelta(days=30), "Critical ?": "No", "Total Float": 0.0, "Comments": "Blueprint approved", "Project Manager": "Jane Doe"},
        # Phase 2 - In Progress
        {"Level": 1, "Task Name": "Build & Configuration Phase", "Status": "In Progress", "% Complete": 0.70, "Schedule Health": "Green", "Start Date": today - timedelta(days=30), "End Date": today + timedelta(days=30), "Baseline Start": today - timedelta(days=30), "Baseline Finish": today + timedelta(days=30), "Critical ?": "Yes", "Total Float": 5.0, "Comments": "Build is moving smoothly", "Project Manager": "Jane Doe"},
        {"Level": 2, "Task Name": "Core S2P Configuration", "Status": "In Progress", "% Complete": 0.85, "Schedule Health": "Green", "Start Date": today - timedelta(days=30), "End Date": today + timedelta(days=10), "Baseline Start": today - timedelta(days=30), "Baseline Finish": today + timedelta(days=10), "Critical ?": "Yes", "Total Float": 5.0, "Comments": "Configurations on track", "Project Manager": "Jane Doe"},
        {"Level": 2, "Task Name": "Integration Setup", "Status": "In Progress", "% Complete": 0.40, "Schedule Health": "Green", "Start Date": today + timedelta(days=1), "End Date": today + timedelta(days=30), "Baseline Start": today + timedelta(days=1), "Baseline Finish": today + timedelta(days=30), "Critical ?": "Yes", "Total Float": 12.0, "Comments": "APIs are mapped", "Project Manager": "Jane Doe"},
        # Phase 3 - Future
        {"Level": 1, "Task Name": "Testing & UAT Phase", "Status": "Not Started", "% Complete": None, "Schedule Health": "", "Start Date": today + timedelta(days=31), "End Date": today + timedelta(days=75), "Baseline Start": today + timedelta(days=31), "Baseline Finish": today + timedelta(days=75), "Critical ?": "No", "Total Float": 15.0, "Comments": "Preparation started", "Project Manager": "Jane Doe"},
        {"Level": 1, "Task Name": "Go-Live Preparation", "Status": "Not Started", "% Complete": None, "Schedule Health": "", "Start Date": today + timedelta(days=76), "End Date": today + timedelta(days=120), "Baseline Start": today + timedelta(days=76), "Baseline Finish": today + timedelta(days=120), "Critical ?": "No", "Total Float": 20.0, "Comments": "Planned", "Project Manager": "Jane Doe"}
    ]
    green_comments = [
        {"row_ref": "Row 2", "text": "Project dashboard updated, status remains green. Team is executing blueprint items as scheduled.", "author": "Jane Doe", "date": today},
        {"row_ref": "Row 6", "text": "Core S2P config is nearing completion. Client team has approved early testing.", "author": "Jane Doe", "date": today - timedelta(days=3)}
    ]
    create_workbook(
        input_dir / "Test_Plan_Green.xlsx",
        "Zycus - Green Implementation",
        "Jane Doe",
        "Green",
        "Low",
        "Build & Configuration Phase",
        0.60,
        green_tasks,
        green_comments,
    )

    # ------------------ AMBER PLAN ------------------
    amber_tasks = [
        # Root project
        {"Level": 0, "Task Name": "Zycus - Amber Implementation Project", "Status": "In Progress", "% Complete": 0.45, "Schedule Health": "Amber", "Start Date": today - timedelta(days=60), "End Date": today + timedelta(days=120), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today + timedelta(days=120), "Critical ?": "Yes", "Total Float": 0.0, "Comments": "Experiencing minor delays in Integration configuration", "Project Manager": "John Smith"},
        # Phase 1 - Completed
        {"Level": 1, "Task Name": "Design & Blueprint Phase", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Green", "Start Date": today - timedelta(days=60), "End Date": today - timedelta(days=30), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today - timedelta(days=30), "Critical ?": "No", "Total Float": 0.0, "Comments": "Completed on time", "Project Manager": "John Smith"},
        # Phase 2 - In Progress with minor delay
        {"Level": 1, "Task Name": "Build & Configuration Phase", "Status": "In Progress", "% Complete": 0.50, "Schedule Health": "Yellow", "Start Date": today - timedelta(days=30), "End Date": today + timedelta(days=30), "Baseline Start": today - timedelta(days=30), "Baseline Finish": today + timedelta(days=30), "Critical ?": "Yes", "Total Float": -2.0, "Comments": "Integration delays with Client ERP", "Project Manager": "John Smith"},
        {"Level": 2, "Task Name": "Core S2P Configuration", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Green", "Start Date": today - timedelta(days=30), "End Date": today - timedelta(days=5), "Baseline Start": today - timedelta(days=30), "Baseline Finish": today - timedelta(days=5), "Critical ?": "Yes", "Total Float": 0.0, "Comments": "Completed config", "Project Manager": "John Smith"},
        # Late active task
        {"Level": 2, "Task Name": "ERP Integration Mapping", "Status": "In Progress", "% Complete": 0.40, "Schedule Health": "Red", "Start Date": today - timedelta(days=20), "End Date": today - timedelta(days=2), "Baseline Start": today - timedelta(days=20), "Baseline Finish": today - timedelta(days=2), "Critical ?": "Yes", "Total Float": -5.0, "Comments": "Late active task due to API schema change from client ERP.", "Project Manager": "John Smith"},
        {"Level": 2, "Task Name": "Data Migration Setup", "Status": "In Progress", "% Complete": 0.30, "Schedule Health": "Yellow", "Start Date": today - timedelta(days=10), "End Date": today + timedelta(days=30), "Baseline Start": today - timedelta(days=10), "Baseline Finish": today + timedelta(days=30), "Critical ?": "No", "Total Float": 5.0, "Comments": "Minor delay on master data upload", "Project Manager": "John Smith"},
        # Phase 3
        {"Level": 1, "Task Name": "Testing & UAT Phase", "Status": "Not Started", "% Complete": None, "Schedule Health": "", "Start Date": today + timedelta(days=31), "End Date": today + timedelta(days=75), "Baseline Start": today + timedelta(days=31), "Baseline Finish": today + timedelta(days=75), "Critical ?": "No", "Total Float": 5.0, "Comments": "Planned", "Project Manager": "John Smith"}
    ]
    amber_comments = [
        {"row_ref": "Row 6", "text": "ERP integration has hit a slight dependency block. We need the client ERP specialist to confirm the API headers.", "author": "John Smith", "date": today},
        {"row_ref": "Row 7", "text": "Master data templates have been shared. Clean up is pending from client side.", "author": "John Smith", "date": today - timedelta(days=2)}
    ]
    create_workbook(
        input_dir / "Test_Plan_Amber.xlsx",
        "Zycus - Amber Implementation",
        "John Smith",
        "Amber",
        "Medium",
        "Build & Configuration Phase",
        0.45,
        amber_tasks,
        amber_comments,
    )

    # ------------------ RED PLAN ------------------
    red_tasks = [
        # Root project
        {"Level": 0, "Task Name": "Zycus - Red Implementation Project", "Status": "In Progress", "% Complete": 0.20, "Schedule Health": "Red", "Start Date": today - timedelta(days=60), "End Date": today + timedelta(days=120), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today + timedelta(days=120), "Critical ?": "Yes", "Total Float": -15.0, "Comments": "Significant delays across integration and testing start. Project is severely at risk.", "Project Manager": "Alice Johnson"},
        # Phase 1 - Completed but late
        {"Level": 1, "Task Name": "Design & Blueprint Phase", "Status": "Completed", "% Complete": 1.0, "Schedule Health": "Yellow", "Start Date": today - timedelta(days=60), "End Date": today - timedelta(days=20), "Baseline Start": today - timedelta(days=60), "Baseline Finish": today - timedelta(days=40), "Critical ?": "No", "Total Float": -10.0, "Comments": "Completed 20 days late", "Project Manager": "Alice Johnson"},
        # Phase 2 - Severely delayed
        {"Level": 1, "Task Name": "Build & Configuration Phase", "Status": "In Progress", "% Complete": 0.25, "Schedule Health": "Red", "Start Date": today - timedelta(days=20), "End Date": today + timedelta(days=20), "Baseline Start": today - timedelta(days=40), "Baseline Finish": today + timedelta(days=10), "Critical ?": "Yes", "Total Float": -18.0, "Comments": "Build is blocked by integration failures", "Project Manager": "Alice Johnson"},
        # Multiple late active tasks & blockers
        {"Level": 2, "Task Name": "Core S2P Configuration", "Status": "In Progress", "% Complete": 0.35, "Schedule Health": "Red", "Start Date": today - timedelta(days=20), "End Date": today - timedelta(days=5), "Baseline Start": today - timedelta(days=40), "Baseline Finish": today - timedelta(days=15), "Critical ?": "Yes", "Total Float": -15.0, "Comments": "Late active task. Blocked on middleware server setup.", "Project Manager": "Alice Johnson"},
        {"Level": 2, "Task Name": "ERP Integration Mapping", "Status": "In Progress", "% Complete": 0.10, "Schedule Health": "Red", "Start Date": today - timedelta(days=15), "End Date": today - timedelta(days=1), "Baseline Start": today - timedelta(days=30), "Baseline Finish": today - timedelta(days=5), "Critical ?": "Yes", "Total Float": -20.0, "Comments": "Late active task. Blocked on network credentials and ports.", "Project Manager": "Alice Johnson"},
        {"Level": 2, "Task Name": "UAT Script Writing", "Status": "In Progress", "% Complete": 0.10, "Schedule Health": "Yellow", "Start Date": today - timedelta(days=10), "End Date": today + timedelta(days=10), "Baseline Start": today - timedelta(days=20), "Baseline Finish": today + timedelta(days=5), "Critical ?": "No", "Total Float": -12.0, "Comments": "Scripts are delayed as configuration isn't completed.", "Project Manager": "Alice Johnson"},
        # Phase 3 - Missed start date
        {"Level": 1, "Task Name": "Testing & UAT Phase", "Status": "Not Started", "% Complete": 0.0, "Schedule Health": "Red", "Start Date": today - timedelta(days=2), "End Date": today + timedelta(days=40), "Baseline Start": today - timedelta(days=10), "Baseline Finish": today + timedelta(days=30), "Critical ?": "Yes", "Total Float": -18.0, "Comments": "UAT launch missed start date by 2 days.", "Project Manager": "Alice Johnson"}
    ]
    red_comments = [
        {"row_ref": "Row 4", "text": "Severe blocker: Integration with client JDE system is failing. Client has not opened necessary firewall ports.", "author": "Alice Johnson", "date": today},
        {"row_ref": "Row 5", "text": "Network ports still blocked. Escalate to VP for network credentials.", "author": "Alice Johnson", "date": today - timedelta(days=1)}
    ]
    create_workbook(
        input_dir / "Test_Plan_Red.xlsx",
        "Zycus - Red Implementation",
        "Alice Johnson",
        "Red",
        "High",
        "Build & Configuration Phase",
        0.20,
        red_tasks,
        red_comments,
    )

if __name__ == "__main__":
    generate_all_test_plans()
