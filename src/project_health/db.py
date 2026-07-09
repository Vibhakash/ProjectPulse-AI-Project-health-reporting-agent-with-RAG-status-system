from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_file TEXT NOT NULL,
    project_manager TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, source_file)
);

CREATE TABLE IF NOT EXISTS project_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    run_date TEXT NOT NULL,
    rag_status TEXT NOT NULL,
    rag_score REAL NOT NULL,
    confidence TEXT NOT NULL,
    data_quality_score REAL NOT NULL,
    source_schedule_health TEXT,
    project_stage TEXT,
    summary_json TEXT NOT NULL,
    weekly_json_path TEXT,
    weekly_markdown_path TEXT,
    rag_flip_alert TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    source_file TEXT NOT NULL,
    sheet_name TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    parent_source_row INTEGER,
    project_name TEXT,
    project_category TEXT,
    ancestors TEXT,
    project_manager TEXT,
    level INTEGER,
    phase_milestone TEXT,
    area TEXT,
    at_risk TEXT,
    source_schedule_health TEXT,
    task_name TEXT,
    status TEXT,
    percent_complete REAL,
    start_date TEXT,
    end_date TEXT,
    baseline_start TEXT,
    baseline_finish TEXT,
    baseline_start_date TEXT,
    baseline_end_date TEXT,
    baseline_start2 TEXT,
    baseline_finish2 TEXT,
    variance REAL,
    variance2 REAL,
    duration REAL,
    total_float REAL,
    critical INTEGER,
    priority TEXT,
    owner TEXT,
    ownership TEXT,
    assigned_to TEXT,
    predecessors TEXT,
    description TEXT,
    status_comment TEXT,
    comments TEXT,
    on_hold INTEGER,
    not_applicable INTEGER,
    start TEXT,
    finish TEXT,
    rag TEXT,
    days_until_today REAL,
    no_of_days REAL,
    target_start_to_today REAL,
    raw_data_json TEXT NOT NULL,
    FOREIGN KEY(snapshot_id) REFERENCES project_snapshots(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    source_file TEXT NOT NULL,
    sheet_name TEXT,
    source_row INTEGER,
    referenced_row INTEGER,
    comment_text TEXT NOT NULL,
    author TEXT,
    created_at_source TEXT,
    raw_data_json TEXT NOT NULL,
    FOREIGN KEY(snapshot_id) REFERENCES project_snapshots(id)
);

CREATE TABLE IF NOT EXISTS rag_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    signal_name TEXT NOT NULL,
    weight REAL NOT NULL,
    raw_value TEXT NOT NULL,
    score REAL NOT NULL,
    weighted_score REAL NOT NULL,
    evidence_json TEXT NOT NULL,
    triggered_override INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(snapshot_id) REFERENCES project_snapshots(id)
);

CREATE TABLE IF NOT EXISTS data_quality_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    sheet_name TEXT,
    row_number INTEGER,
    column_name TEXT,
    FOREIGN KEY(snapshot_id) REFERENCES project_snapshots(id)
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
