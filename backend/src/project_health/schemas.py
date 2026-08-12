from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class DataQualityIssue:
    severity: str
    message: str
    sheet_name: str | None = None
    row_number: int | None = None
    column_name: str | None = None


@dataclass
class TaskRecord:
    source_file: str
    sheet_name: str
    source_row: int
    raw_data: dict[str, Any]
    project_name: str | None = None
    project_category: str | None = None
    ancestors: str | None = None
    parent_source_row: int | None = None
    project_manager: str | None = None
    level: int | None = None
    phase_milestone: str | None = None
    area: str | None = None
    at_risk: str | None = None
    source_schedule_health: str | None = None
    task_name: str | None = None
    status: str | None = None
    percent_complete: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    baseline_start: date | None = None
    baseline_finish: date | None = None
    baseline_start_date: date | None = None
    baseline_end_date: date | None = None
    baseline_start2: date | None = None
    baseline_finish2: date | None = None
    variance: float | None = None
    variance2: float | None = None
    duration: float | None = None
    total_float: float | None = None
    critical: bool | None = None
    priority: str | None = None
    owner: str | None = None
    ownership: str | None = None
    assigned_to: str | None = None
    predecessors: str | None = None
    description: str | None = None
    status_comment: str | None = None
    comments: str | None = None
    on_hold: bool | None = None
    not_applicable: bool | None = None
    start: date | None = None
    finish: date | None = None
    rag: str | None = None
    days_until_today: float | None = None
    no_of_days: float | None = None
    target_start_to_today: float | None = None


@dataclass
class CommentRecord:
    source_file: str
    sheet_name: str
    source_row: int
    referenced_row: int | None
    comment_text: str
    author: str | None = None
    created_at: datetime | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectWorkbook:
    source_file: str
    detected_project_name: str
    task_sheet: str
    summary: dict[str, Any]
    tasks: list[TaskRecord]
    comments: list[CommentRecord]
    data_quality_issues: list[DataQualityIssue]
    all_task_columns: list[str]


@dataclass
class RagSignal:
    name: str
    weight: float
    raw_value: str
    score: float
    weighted_score: float
    evidence: list[str] = field(default_factory=list)
    triggered_override: bool = False


@dataclass
class RagResult:
    project_name: str
    status: str
    score: float
    confidence: str
    data_quality_score: float
    source_schedule_health: str | None
    signals: list[RagSignal]
    reasons: list[str]
    top_risks: list[str]
    recommendations: list[str]
    caveats: list[str]
    executive_summary: str | None = None
    sentiment_summary: str | None = None
    risk_themes: list[str] = field(default_factory=list)
    agent_mode: str = "offline"
    rag_flip_alert: str | None = None
