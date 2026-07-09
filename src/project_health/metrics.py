from __future__ import annotations

from collections import Counter
from datetime import date

from .schemas import ProjectWorkbook, TaskRecord


def project_metrics(workbook: ProjectWorkbook, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    tasks = [task for task in workbook.tasks if task.task_name]
    active = [task for task in tasks if (task.status or "").lower() not in {"completed", "complete"}]
    milestones = [task for task in tasks if _is_milestone(task)]

    health_counts = Counter((task.source_schedule_health or "Unknown").title() for task in tasks)
    status_counts = Counter((task.status or "Unknown").title() for task in tasks)
    avg_complete = _avg([task.percent_complete for task in tasks])
    project_start = _min_date([task.start_date or task.start for task in tasks])
    project_end = _max_date([task.end_date or task.finish for task in tasks])
    expected_progress = _expected_progress(project_start, project_end, as_of)

    late_tasks = [
        task for task in active
        if (task.end_date or task.finish) and (task.end_date or task.finish) < as_of
    ]
    red_or_yellow = [
        task for task in tasks
        if (task.source_schedule_health or "").strip().lower() in {"red", "yellow", "amber"}
    ]
    critical_negative_float = [
        task for task in tasks
        if task.critical or (task.total_float is not None and task.total_float < 0)
    ]
    blocker_text_tasks = [
        task for task in tasks
        if _has_blocker_text(" ".join([task.status_comment or "", task.comments or "", task.task_name or ""]))
    ]

    return {
        "task_count": len(tasks),
        "active_task_count": len(active),
        "milestone_count": len(milestones),
        "health_counts": dict(health_counts),
        "status_counts": dict(status_counts),
        "average_percent_complete": avg_complete,
        "expected_progress": expected_progress,
        "progress_gap": None if expected_progress is None or avg_complete is None else round(expected_progress - avg_complete, 2),
        "project_start": project_start.isoformat() if project_start else None,
        "project_end": project_end.isoformat() if project_end else None,
        "late_tasks": _task_refs(late_tasks[:10]),
        "red_or_yellow_tasks": _task_refs(red_or_yellow[:10]),
        "critical_negative_float_tasks": _task_refs(critical_negative_float[:10]),
        "blocker_text_tasks": _task_refs(blocker_text_tasks[:10]),
        "comment_count": len(workbook.comments),
        "summary": workbook.summary,
    }


def source_project_health(workbook: ProjectWorkbook) -> str | None:
    for task in workbook.tasks:
        if task.level in (0, None) and task.source_schedule_health:
            return task.source_schedule_health.title()
    for task in workbook.tasks:
        if task.source_schedule_health:
            return task.source_schedule_health.title()
    return None


def data_quality_score(workbook: ProjectWorkbook) -> float:
    expected = ["Task Name", "Status", "% Complete", "Schedule Health", "Start Date", "End Date"]
    present_ratio = sum(1 for col in expected if col in workbook.all_task_columns) / len(expected)
    warning_penalty = min(0.35, len([i for i in workbook.data_quality_issues if i.severity == "warning"]) * 0.01)
    comments_bonus = 0.1 if workbook.comments else 0
    baseline_bonus = 0.1 if any(t.baseline_start or t.baseline_finish or t.baseline_start_date or t.baseline_end_date for t in workbook.tasks) else 0
    score = (present_ratio * 0.8) + comments_bonus + baseline_bonus - warning_penalty
    return round(max(0, min(1, score)) * 100, 1)


def _is_milestone(task: TaskRecord) -> bool:
    if task.phase_milestone:
        return True
    if task.duration == 0:
        return True
    return task.level is not None and task.level <= 1


def _expected_progress(start: date | None, end: date | None, as_of: date) -> float | None:
    if not start or not end or end <= start:
        return None
    if as_of <= start:
        return 0
    if as_of >= end:
        return 100
    total = (end - start).days
    elapsed = (as_of - start).days
    return round((elapsed / total) * 100, 2)


def _avg(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 2)


def _min_date(values: list[date | None]) -> date | None:
    dates = [v for v in values if v]
    return min(dates) if dates else None


def _max_date(values: list[date | None]) -> date | None:
    dates = [v for v in values if v]
    return max(dates) if dates else None


def _has_blocker_text(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in ["blocked", "pending", "delay", "impacted", "remain", "risk", "issue", "need"])


def _task_refs(tasks: list[TaskRecord]) -> list[dict]:
    return [
        {
            "row": task.source_row,
            "task": task.task_name,
            "health": task.source_schedule_health,
            "status": task.status,
            "percent_complete": task.percent_complete,
        }
        for task in tasks
    ]
