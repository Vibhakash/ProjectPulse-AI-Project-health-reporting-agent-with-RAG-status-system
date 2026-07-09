from __future__ import annotations

import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from .config import FIELD_ALIASES
from .excel_reader import read_workbook
from .schemas import CommentRecord, DataQualityIssue, ProjectWorkbook, TaskRecord

UNPARSEABLE = "#UNPARSEABLE"
EXCEL_EPOCH = date(1899, 12, 30)


def load_project_workbook(path: str | Path, run_date: date | None = None) -> ProjectWorkbook:
    source = Path(path)
    sheets = read_workbook(source)
    issues: list[DataQualityIssue] = []
    task_sheet_name = _detect_task_sheet(sheets)
    summary_sheet_name = _detect_summary_sheet(sheets)
    comments_sheet_name = _detect_comments_sheet(sheets)

    if not task_sheet_name:
        raise ValueError(f"No task sheet found in {source}")

    task_rows = sheets[task_sheet_name]
    all_columns = sorted({key for row in task_rows for key in row if not key.startswith("__")})
    tasks = [_normalize_task(source.name, task_sheet_name, row, issues) for row in task_rows]
    _assign_hierarchy(tasks)

    summary = _normalize_summary(sheets.get(summary_sheet_name or "", []), issues, summary_sheet_name)
    comments = _normalize_comments(source.name, comments_sheet_name, sheets.get(comments_sheet_name or "", []), issues)

    if not summary.get("Project Stage"):
        ref_date = run_date or date.today()
        summary["Project Stage"] = _detect_project_stage_fallback(tasks, ref_date)

    project_name = _detect_project_name(source.stem, tasks, summary)
    _add_completeness_issues(tasks, comments, all_columns, issues, task_sheet_name)

    return ProjectWorkbook(
        source_file=str(source),
        detected_project_name=project_name,
        task_sheet=task_sheet_name,
        summary=summary,
        tasks=tasks,
        comments=comments,
        data_quality_issues=issues,
        all_task_columns=all_columns,
    )


def _detect_task_sheet(sheets: dict[str, list[dict[str, Any]]]) -> str | None:
    best_name = None
    best_score = -1
    expected = {"Task Name", "Status", "% Complete", "Schedule Health"}
    for name, rows in sheets.items():
        columns = {key for row in rows[:5] for key in row}
        score = len(expected & columns)
        if score > best_score:
            best_name, best_score = name, score
    return best_name if best_score >= 2 else None


def _detect_summary_sheet(sheets: dict[str, list[dict[str, Any]]]) -> str | None:
    for name in sheets:
        if name.lower().strip() == "summary":
            return name
    return None


def _detect_comments_sheet(sheets: dict[str, list[dict[str, Any]]]) -> str | None:
    for name in sheets:
        if "comment" in name.lower():
            return name
    return None


def _normalize_task(source_file: str, sheet_name: str, row: dict[str, Any], issues: list[DataQualityIssue]) -> TaskRecord:
    cleaned = {key: _clean_value(value, issues, sheet_name, row.get("__row_number__"), key) for key, value in row.items() if not key.startswith("__")}
    record = TaskRecord(
        source_file=source_file,
        sheet_name=sheet_name,
        source_row=int(row.get("__row_number__", 0)),
        raw_data=cleaned,
    )
    for attr, aliases in FIELD_ALIASES.items():
        value = _first(cleaned, aliases)
        if attr in {
            "start_date",
            "end_date",
            "baseline_start",
            "baseline_finish",
            "baseline_start_date",
            "baseline_end_date",
            "baseline_start2",
            "baseline_finish2",
            "start",
            "finish",
        }:
            setattr(record, attr, _to_date(value, issues, sheet_name, record.source_row, aliases[0]))
        elif attr in {"percent_complete"}:
            setattr(record, attr, _to_percent(value))
        elif attr in {"level"}:
            setattr(record, attr, _to_int(value))
        elif attr in {"variance", "variance2", "duration", "total_float", "days_until_today", "no_of_days", "target_start_to_today"}:
            setattr(record, attr, _to_float(value))
        elif attr in {"critical", "on_hold", "not_applicable"}:
            setattr(record, attr, _to_bool(value))
        else:
            setattr(record, attr, _to_text(value))
    return record


def _assign_hierarchy(tasks: list[TaskRecord]) -> None:
    stack: dict[int, TaskRecord] = {}
    for task in tasks:
        if task.level is None:
            task.parent_source_row = _parent_from_ancestors(task.ancestors)
            continue
        parent = stack.get(task.level - 1)
        task.parent_source_row = parent.source_row if parent else _parent_from_ancestors(task.ancestors)
        stack[task.level] = task
        for level in list(stack):
            if level > task.level:
                del stack[level]


def _parent_from_ancestors(value: str | None) -> int | None:
    if not value:
        return None
    numbers = re.findall(r"\d+", value)
    return int(numbers[-1]) if numbers else None


def _normalize_summary(rows: list[dict[str, Any]], issues: list[DataQualityIssue], sheet_name: str | None) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for row in rows:
        values = [v for k, v in row.items() if not k.startswith("__")]
        if not values:
            continue
        key = _to_text(_clean_value(values[0], issues, sheet_name, row.get("__row_number__"), None))
        value = _clean_value(values[1], issues, sheet_name, row.get("__row_number__"), key) if len(values) > 1 else None
        if key:
            summary[key] = _serialize(value)
    return summary


def _normalize_comments(
    source_file: str,
    sheet_name: str | None,
    rows: list[dict[str, Any]],
    issues: list[DataQualityIssue],
) -> list[CommentRecord]:
    if not sheet_name or not rows:
        issues.append(DataQualityIssue("info", "No stakeholder comments available.", sheet_name))
        return []
    comments: list[CommentRecord] = []
    for row in rows:
        values = [value for key, value in row.items() if not key.startswith("__")]
        if len(values) < 2:
            continue
        ref_text = _to_text(values[0])
        comment_text = _to_text(values[1])
        if not comment_text:
            continue
        comments.append(
            CommentRecord(
                source_file=source_file,
                sheet_name=sheet_name,
                source_row=int(row.get("__row_number__", 0)),
                referenced_row=_extract_row_reference(ref_text),
                comment_text=comment_text,
                author=_to_text(values[2]) if len(values) > 2 else None,
                created_at=_to_datetime(values[3]) if len(values) > 3 else None,
                raw_data={f"col_{idx+1}": _serialize(value) for idx, value in enumerate(values)},
            )
        )
    if not comments:
        issues.append(DataQualityIssue("info", "Comments sheet exists but contains no usable comments.", sheet_name))
    return comments


def _detect_project_name(fallback: str, tasks: list[TaskRecord], summary: dict[str, Any]) -> str:
    for key in ("Project Name", "Project"):
        if summary.get(key):
            return str(summary[key])
    for task in tasks:
        if task.level in (None, 0) and task.task_name:
            return task.task_name
    for task in tasks:
        if task.task_name:
            return task.task_name
    return fallback


def _add_completeness_issues(
    tasks: list[TaskRecord],
    comments: list[CommentRecord],
    all_columns: list[str],
    issues: list[DataQualityIssue],
    sheet_name: str,
) -> None:
    required = ["Task Name", "Status", "% Complete", "Schedule Health"]
    for column in required:
        if column not in all_columns:
            issues.append(DataQualityIssue("warning", f"Expected column missing: {column}", sheet_name, None, column))
    if not any(t.baseline_start or t.baseline_finish or t.baseline_start_date or t.baseline_end_date for t in tasks):
        issues.append(DataQualityIssue("info", "Baseline dates are incomplete; schedule scoring will fall back to current dates and row health.", sheet_name))
    if not comments:
        issues.append(DataQualityIssue("info", "Stakeholder sentiment confidence reduced because no comments were available.", sheet_name))


def _first(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        if alias in row:
            return row[alias]
    return None


def _clean_value(value: Any, issues: list[DataQualityIssue], sheet: str | None, row: int | None, column: str | None) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        stripped = re.sub(r"\s+", " ", value).strip()
        if stripped == UNPARSEABLE:
            issues.append(DataQualityIssue("warning", "Cell contained #UNPARSEABLE and was treated as unknown.", sheet, row, column))
            return None
        return stripped or None
    return value


def _to_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1", "critical"}:
        return True
    if text in {"false", "no", "n", "0"}:
        return False
    return None


def _to_percent(value: Any) -> float | None:
    number = _to_float(value)
    if number is None:
        return None
    if number <= 1:
        return round(number * 100, 2)
    return round(number, 2)


def _to_date(value: Any, issues: list[DataQualityIssue], sheet: str, row: int, column: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        if 20000 < float(value) < 70000:
            return EXCEL_EPOCH + timedelta(days=int(value))
        return None
    text = str(value).strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    if text:
        issues.append(DataQualityIssue("warning", f"Could not parse date value: {text}", sheet, row, column))
    return None


def _to_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    text = str(value).strip()
    for fmt in ("%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def _extract_row_reference(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def _serialize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _detect_project_stage_fallback(tasks: list[TaskRecord], ref_date: date) -> str:
    # Identify parent tasks (summary tasks)
    parent_rows = {t.parent_source_row for t in tasks if t.parent_source_row is not None}
    
    candidates = []
    for t in tasks:
        # Must be a parent task
        if t.source_row not in parent_rows:
            continue
        # Must be level 1 or 2
        if t.level not in (1, 2):
            continue
            
        # Must not be 100% complete
        is_complete = False
        if t.percent_complete is not None:
            if t.percent_complete >= 100.0:
                is_complete = True
        if t.status and t.status.strip().lower() in ("completed", "complete", "done"):
            is_complete = True
            
        if is_complete:
            continue
            
        # Check active status or dates
        in_progress = t.status and t.status.strip().lower() in ("in progress", "in-progress", "active")
        active_dates = False
        if t.start_date and t.end_date:
            if t.start_date <= ref_date <= t.end_date:
                active_dates = True
                
        if in_progress or active_dates:
            candidates.append(t)
            
    # Sort candidates by level (prefer level 1 over level 2) then by source_row (earlier phase)
    if candidates:
        candidates.sort(key=lambda x: (x.level or 99, x.source_row))
        if candidates[0].task_name:
            return candidates[0].task_name
            
    # Fallback 1: Any level 1 or 2 parent task that is not 100% complete
    for t in tasks:
        if t.level in (1, 2) and t.source_row in parent_rows:
            is_complete = False
            if t.percent_complete is not None and t.percent_complete >= 100.0:
                is_complete = True
            if t.status and t.status.strip().lower() in ("completed", "complete", "done"):
                is_complete = True
            if not is_complete and t.task_name:
                return t.task_name
                
    # Fallback 2: Any level 1 parent task
    for t in tasks:
        if t.level == 1 and t.source_row in parent_rows and t.task_name:
            return t.task_name
            
    return "Unknown"
