from __future__ import annotations

import json
import sqlite3
from datetime import date
from typing import Any

from .schemas import ProjectWorkbook, RagResult


def save_analysis(conn: sqlite3.Connection, workbook: ProjectWorkbook, result: RagResult, output_paths: dict[str, str], run_date: date) -> int:
    manager = _first_non_empty([task.project_manager for task in workbook.tasks])
    project_id = _upsert_project(conn, workbook.detected_project_name, workbook.source_file, manager)
    previous = latest_snapshot_for_project(conn, project_id)
    flip_alert = _flip_alert(previous["rag_status"] if previous else None, result.status)
    result.rag_flip_alert = flip_alert

    cursor = conn.execute(
        """
        INSERT INTO project_snapshots (
            project_id, run_date, rag_status, rag_score, confidence, data_quality_score,
            source_schedule_health, project_stage, summary_json, weekly_json_path,
            weekly_markdown_path, rag_flip_alert
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            run_date.isoformat(),
            result.status,
            result.score,
            result.confidence,
            result.data_quality_score,
            result.source_schedule_health,
            str(workbook.summary.get("Project Stage") or ""),
            json.dumps(workbook.summary, default=str),
            output_paths.get("json"),
            output_paths.get("markdown"),
            flip_alert,
        ),
    )
    snapshot_id = int(cursor.lastrowid)
    _insert_tasks(conn, snapshot_id, workbook)
    _insert_comments(conn, snapshot_id, workbook)
    _insert_signals(conn, snapshot_id, result)
    _insert_quality_issues(conn, snapshot_id, workbook)
    conn.commit()
    return snapshot_id


def latest_snapshot_for_project(conn: sqlite3.Connection, project_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM project_snapshots WHERE project_id = ? ORDER BY run_date DESC, id DESC LIMIT 1",
        (project_id,),
    ).fetchone()


def fetch_portfolio(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT ps.*, p.name, p.source_file, p.project_manager
            FROM project_snapshots ps
            JOIN projects p ON p.id = ps.project_id
            WHERE ps.id IN (
                SELECT MAX(id) FROM project_snapshots GROUP BY project_id
            )
            ORDER BY ps.rag_score DESC
            """
        )
    )


def fetch_snapshots(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT ps.*, p.name, p.source_file, p.project_manager
            FROM project_snapshots ps
            JOIN projects p ON p.id = ps.project_id
            ORDER BY ps.run_date ASC, p.name ASC
            """
        )
    )


def fetch_top_risk_tasks(conn: sqlite3.Connection, limit: int = 10) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT p.name, t.task_name, t.source_row, t.source_schedule_health, t.status,
                   t.percent_complete, t.total_float, t.critical, t.status_comment,
                   ps.rag_status
            FROM tasks t
            JOIN project_snapshots ps ON ps.id = t.snapshot_id
            JOIN projects p ON p.id = ps.project_id
            WHERE lower(coalesce(t.source_schedule_health, '')) IN ('red', 'yellow', 'amber')
               OR (t.critical = 1 AND lower(coalesce(t.status, '')) NOT IN ('completed', 'complete'))
               OR t.total_float < 0
               OR lower(coalesce(t.status_comment, '')) LIKE '%pending%'
               OR lower(coalesce(t.status_comment, '')) LIKE '%delay%'
            ORDER BY t.critical DESC, t.total_float ASC, ps.rag_score DESC
            LIMIT ?
            """,
            (limit,),
        )
    )


def fetch_comment_themes(conn: sqlite3.Connection, limit: int = 20) -> list[str]:
    rows = conn.execute("SELECT comment_text FROM comments ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [row["comment_text"] for row in rows]


def simple_query(conn: sqlite3.Connection, question: str) -> list[sqlite3.Row]:
    q = question.lower()
    if "blocked" in q or "dependency" in q or "external" in q:
        return fetch_top_risk_tasks(conn, 20)
    if "red" in q:
        return list(conn.execute("SELECT p.name, ps.rag_status, ps.rag_score FROM project_snapshots ps JOIN projects p ON p.id=ps.project_id WHERE ps.rag_status='Red'"))
    return fetch_portfolio(conn)


def _upsert_project(conn: sqlite3.Connection, name: str, source_file: str, manager: str | None) -> int:
    conn.execute(
        "INSERT OR IGNORE INTO projects (name, source_file, project_manager) VALUES (?, ?, ?)",
        (name, source_file, manager),
    )
    if manager:
        conn.execute("UPDATE projects SET project_manager = ?, source_file = ? WHERE name = ?", (manager, source_file, name))
    else:
        conn.execute("UPDATE projects SET source_file = ? WHERE name = ?", (source_file, name))
    
    row = conn.execute("SELECT id FROM projects WHERE name = ?", (name,)).fetchone()
    return int(row["id"])


def _insert_tasks(conn: sqlite3.Connection, snapshot_id: int, workbook: ProjectWorkbook) -> None:
    for task in workbook.tasks:
        conn.execute(
            """
            INSERT INTO tasks (
                snapshot_id, source_file, sheet_name, source_row, parent_source_row, project_name,
                project_category, ancestors, project_manager, level, phase_milestone, area,
                at_risk, source_schedule_health, task_name, status, percent_complete, start_date,
                end_date, baseline_start, baseline_finish, baseline_start_date, baseline_end_date,
                baseline_start2, baseline_finish2, variance, variance2, duration, total_float,
                critical, priority, owner, ownership, assigned_to, predecessors, description,
                status_comment, comments, on_hold, not_applicable, start, finish, rag,
                days_until_today, no_of_days, target_start_to_today, raw_data_json
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                snapshot_id,
                task.source_file,
                task.sheet_name,
                task.source_row,
                task.parent_source_row,
                task.project_name,
                task.project_category,
                task.ancestors,
                task.project_manager,
                task.level,
                task.phase_milestone,
                task.area,
                task.at_risk,
                task.source_schedule_health,
                task.task_name,
                task.status,
                task.percent_complete,
                _iso(task.start_date),
                _iso(task.end_date),
                _iso(task.baseline_start),
                _iso(task.baseline_finish),
                _iso(task.baseline_start_date),
                _iso(task.baseline_end_date),
                _iso(task.baseline_start2),
                _iso(task.baseline_finish2),
                task.variance,
                task.variance2,
                task.duration,
                task.total_float,
                _bool(task.critical),
                task.priority,
                task.owner,
                task.ownership,
                task.assigned_to,
                task.predecessors,
                task.description,
                task.status_comment,
                task.comments,
                _bool(task.on_hold),
                _bool(task.not_applicable),
                _iso(task.start),
                _iso(task.finish),
                task.rag,
                task.days_until_today,
                task.no_of_days,
                task.target_start_to_today,
                json.dumps(task.raw_data, default=str),
            ),
        )


def _insert_comments(conn: sqlite3.Connection, snapshot_id: int, workbook: ProjectWorkbook) -> None:
    for comment in workbook.comments:
        conn.execute(
            """
            INSERT INTO comments (
                snapshot_id, source_file, sheet_name, source_row, referenced_row,
                comment_text, author, created_at_source, raw_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                comment.source_file,
                comment.sheet_name,
                comment.source_row,
                comment.referenced_row,
                comment.comment_text,
                comment.author,
                _iso(comment.created_at),
                json.dumps(comment.raw_data, default=str),
            ),
        )


def _insert_signals(conn: sqlite3.Connection, snapshot_id: int, result: RagResult) -> None:
    for signal in result.signals:
        conn.execute(
            """
            INSERT INTO rag_signals (
                snapshot_id, signal_name, weight, raw_value, score, weighted_score,
                evidence_json, triggered_override
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                signal.name,
                signal.weight,
                signal.raw_value,
                signal.score,
                signal.weighted_score,
                json.dumps(signal.evidence, default=str),
                _bool(signal.triggered_override),
            ),
        )


def _insert_quality_issues(conn: sqlite3.Connection, snapshot_id: int, workbook: ProjectWorkbook) -> None:
    for issue in workbook.data_quality_issues:
        conn.execute(
            """
            INSERT INTO data_quality_issues (
                snapshot_id, severity, message, sheet_name, row_number, column_name
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (snapshot_id, issue.severity, issue.message, issue.sheet_name, issue.row_number, issue.column_name),
        )


def _flip_alert(previous: str | None, current: str) -> str | None:
    order = {"Green": 1, "Amber": 2, "Red": 3}
    if previous and order.get(current, 0) > order.get(previous, 0):
        return f"RAG worsened from {previous} to {current}"
    return None


def _first_non_empty(values: list[str | None]) -> str | None:
    for value in values:
        if value:
            return value
    return None


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else value


def _bool(value: bool | None) -> int | None:
    if value is None:
        return None
    return 1 if value else 0
