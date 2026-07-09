"""
FastAPI HTTP server for the Project Health Reporting Agent.

This module is a thin REST wrapper around the existing Python backend functions.
It does NOT re-implement any RAG logic — that stays in rag_engine.py and agent.py.

Endpoints:
  POST /api/analyze            — upload .xlsx files, run RAG + LLM agent
  GET  /api/projects/latest    — portfolio: latest snapshot per project
  GET  /api/snapshots/{id}     — full snapshot detail with signals & agent fields
  GET  /api/snapshots/{id}/tasks    — task evidence rows
  GET  /api/snapshots/{id}/comments — stakeholder comments
  POST /api/monthly-synthesis  — generate monthly PPTX
  GET  /api/files?path=...     — stream a generated output file
  POST /api/ask                — natural-language SQLite query
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

load_dotenv()

# Import existing backend modules (no duplication of logic)
from .cli import run_analyze, run_synthesize
from .db import connect
from .repositories import (
    fetch_portfolio,
    fetch_snapshots,
    simple_query,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH = os.getenv("PROJECT_HEALTH_DB", "storage/project_health.sqlite")
OUTPUT_DIR = "outputs"
ALLOWED_OUTPUT_ROOT = Path(OUTPUT_DIR).resolve()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Project Health Reporting Agent API",
    version="1.0.0",
    description="REST API bridging the Python RAG engine and agent to the React frontend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _db():
    return connect(DB_PATH)


def _row_to_dict(row) -> dict:
    """Convert sqlite3.Row to plain dict."""
    return dict(row) if row else {}


def _rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]


def _parse_json_field(value: Any, default=None):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


# ---------------------------------------------------------------------------
# POST /api/analyze
# ---------------------------------------------------------------------------
@app.post("/api/analyze")
async def analyze(
    files: list[UploadFile] = File(...),
    run_date: str | None = Form(default=None),
):
    """
    Accept one or more .xlsx files, run the full RAG + LLM agent pipeline,
    store results in SQLite, return snapshot summaries.
    """
    # Validate file types
    for f in files:
        if not (f.filename or "").lower().endswith(".xlsx"):
            raise HTTPException(400, f"Only .xlsx files accepted. Got: {f.filename}")

    # Write uploads to a temp directory, run analysis, then clean up
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for f in files:
            dest = tmp_path / (f.filename or "upload.xlsx")
            content = await f.read()
            dest.write_bytes(content)

        try:
            parsed_date = date.fromisoformat(run_date) if run_date else date.today()
        except ValueError:
            parsed_date = date.today()

        try:
            snapshot_ids = run_analyze(
                input_dir=str(tmp_path),
                output_dir=OUTPUT_DIR,
                db_path=DB_PATH,
                config_path=None,
                run_date=parsed_date,
            )
        except Exception as exc:
            raise HTTPException(500, f"Analysis failed: {exc}") from exc

    # Fetch the newly created snapshots from SQLite
    if not snapshot_ids:
        return {"run_date": parsed_date.isoformat(), "snapshots": []}

    conn = _db()
    placeholders = ",".join("?" * len(snapshot_ids))
    rows = conn.execute(
        f"""
        SELECT ps.id AS snapshot_id, ps.project_id, p.name AS project_name,
               ps.rag_status, ps.rag_score, ps.confidence, ps.data_quality_score,
               ps.weekly_markdown_path, ps.weekly_json_path, ps.run_date
        FROM project_snapshots ps
        JOIN projects p ON p.id = ps.project_id
        WHERE ps.id IN ({placeholders})
        ORDER BY ps.id
        """,
        snapshot_ids,
    ).fetchall()
    conn.close()

    snapshots = []
    for row in rows:
        d = _row_to_dict(row)
        # Load agent fields from the stored weekly JSON if available
        agent_fields = _load_agent_fields_from_json(d.get("weekly_json_path"))
        d.update(agent_fields)
        snapshots.append(d)

    return {"run_date": parsed_date.isoformat(), "snapshots": snapshots}


# ---------------------------------------------------------------------------
# GET /api/projects/latest
# ---------------------------------------------------------------------------
@app.get("/api/projects/latest")
def portfolio_latest():
    """Return the latest snapshot for every project (portfolio overview)."""
    conn = _db()
    rows = fetch_portfolio(conn)
    conn.close()
    projects = []
    for row in rows:
        d = _row_to_dict(row)
        projects.append({
            "project_id": d.get("project_id"),
            "snapshot_id": d.get("id"),
            "name": d.get("name"),
            "source_file": d.get("source_file"),
            "project_manager": d.get("project_manager"),
            "run_date": d.get("run_date"),
            "rag_status": d.get("rag_status"),
            "rag_score": d.get("rag_score"),
            "confidence": d.get("confidence"),
            "data_quality_score": d.get("data_quality_score"),
            "source_schedule_health": d.get("source_schedule_health"),
            "project_stage": d.get("project_stage"),
            "rag_flip_alert": d.get("rag_flip_alert"),
            "weekly_markdown_path": d.get("weekly_markdown_path"),
            "weekly_json_path": d.get("weekly_json_path"),
        })
    return {"projects": projects}


# ---------------------------------------------------------------------------
# GET /api/snapshots/{snapshot_id}
# ---------------------------------------------------------------------------
@app.get("/api/snapshots/{snapshot_id}")
def snapshot_detail(snapshot_id: int):
    """
    Full snapshot detail: header metrics, signals with evidence, reasons,
    top risks, recommendations, caveats, and LLM agent fields.
    """
    conn = _db()

    # Snapshot + project header
    snap_row = conn.execute(
        """
        SELECT ps.*, p.name AS project_name, p.source_file, p.project_manager,
               ps.summary_json
        FROM project_snapshots ps
        JOIN projects p ON p.id = ps.project_id
        WHERE ps.id = ?
        """,
        (snapshot_id,),
    ).fetchone()

    if not snap_row:
        conn.close()
        raise HTTPException(404, f"Snapshot {snapshot_id} not found")

    snap = _row_to_dict(snap_row)

    # Load signals from rag_signals table
    sig_rows = conn.execute(
        """
        SELECT signal_name, weight, raw_value, score, weighted_score,
               evidence_json, triggered_override
        FROM rag_signals
        WHERE snapshot_id = ?
        ORDER BY weighted_score DESC
        """,
        (snapshot_id,),
    ).fetchall()
    signals = []
    for sr in sig_rows:
        sd = _row_to_dict(sr)
        sd["evidence"] = _parse_json_field(sd.pop("evidence_json"), [])
        sd["triggered_override"] = bool(sd.get("triggered_override"))
        signals.append(sd)

    # Load task column list from the stored summary_json
    summary = _parse_json_field(snap.get("summary_json"), {})

    # Load stored weekly JSON for reasons / top_risks / recommendations / caveats
    # and the LLM-generated agent fields
    wj_path = snap.get("weekly_json_path")
    stored = _load_stored_weekly_json(wj_path)

    # Distinct task columns from the tasks table for this snapshot
    col_rows = conn.execute(
        "SELECT DISTINCT source_file FROM tasks WHERE snapshot_id = ? LIMIT 1",
        (snapshot_id,),
    ).fetchall()

    all_task_columns = stored.get("all_task_columns", [])

    conn.close()

    return {
        "snapshot": {
            "snapshot_id": snapshot_id,
            "project_name": snap.get("project_name"),
            "run_date": snap.get("run_date"),
            "rag_status": snap.get("rag_status"),
            "rag_score": snap.get("rag_score"),
            "confidence": snap.get("confidence"),
            "data_quality_score": snap.get("data_quality_score"),
            "source_schedule_health": snap.get("source_schedule_health"),
            "project_stage": snap.get("project_stage"),
            "rag_flip_alert": snap.get("rag_flip_alert"),
            # Evidence fields — from stored weekly JSON or defaults
            "reasons": stored.get("reasons", []),
            "top_risks": stored.get("top_risks", []),
            "recommendations": stored.get("recommendations", []),
            "caveats": stored.get("caveats", []),
            # Agent (LLM) fields
            "executive_summary": stored.get("executive_summary"),
            "sentiment_summary": stored.get("sentiment_summary"),
            "risk_themes": stored.get("risk_themes", []),
            "agent_mode": stored.get("agent_mode", "offline"),
            # Signals from DB
            "signals": signals,
            "all_task_columns": all_task_columns,
        }
    }


# ---------------------------------------------------------------------------
# DELETE /api/snapshots/{snapshot_id}
# ---------------------------------------------------------------------------
@app.delete("/api/snapshots/{snapshot_id}")
def delete_snapshot(snapshot_id: int):
    """
    Delete a snapshot, its associated database rows (tasks, comments, signals, quality issues),
    and delete its generated report files on disk.
    """
    conn = _db()

    # 1. Fetch weekly files if they exist to delete them
    row = conn.execute(
        "SELECT weekly_json_path, weekly_markdown_path FROM project_snapshots WHERE id = ?",
        (snapshot_id,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(404, f"Snapshot {snapshot_id} not found")

    for path_field in ("weekly_json_path", "weekly_markdown_path"):
        val = row[path_field]
        if val:
            p = Path(val)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
            # Try relative checking
            p_rel = Path("outputs") / "weekly" / p.name
            if p_rel.exists():
                try:
                    p_rel.unlink()
                except Exception:
                    pass

    # 2. Delete from DB tables
    conn.execute("DELETE FROM tasks WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM comments WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM rag_signals WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM data_quality_issues WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM project_snapshots WHERE id = ?", (snapshot_id,))

    # 3. Clean up orphaned projects
    conn.execute(
        """
        DELETE FROM projects 
        WHERE id NOT IN (SELECT DISTINCT project_id FROM project_snapshots)
        """
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Snapshot {snapshot_id} successfully deleted"}


# ---------------------------------------------------------------------------
# GET /api/snapshots/{snapshot_id}/tasks
# ---------------------------------------------------------------------------
@app.get("/api/snapshots/{snapshot_id}/tasks")
def snapshot_tasks(snapshot_id: int):
    """Return all task evidence rows for a given snapshot."""
    conn = _db()
    rows = conn.execute(
        """
        SELECT source_row, parent_source_row, level, task_name, phase_milestone,
               status, percent_complete, start_date, end_date,
               baseline_start, baseline_finish, variance, total_float,
               critical, on_hold, owner, assigned_to, status_comment,
               source_schedule_health, raw_data_json
        FROM tasks
        WHERE snapshot_id = ?
        ORDER BY source_row
        """,
        (snapshot_id,),
    ).fetchall()
    conn.close()

    tasks = []
    for row in rows:
        d = _row_to_dict(row)
        d["critical"] = bool(d.get("critical"))
        d["on_hold"] = bool(d.get("on_hold"))
        raw = d.pop("raw_data_json", None)
        d["raw_data"] = _parse_json_field(raw, {})
        tasks.append(d)

    return {"tasks": tasks}


# ---------------------------------------------------------------------------
# GET /api/snapshots/{snapshot_id}/comments
# ---------------------------------------------------------------------------
@app.get("/api/snapshots/{snapshot_id}/comments")
def snapshot_comments(snapshot_id: int):
    """Return all stakeholder/PM comments for a given snapshot."""
    conn = _db()
    rows = conn.execute(
        """
        SELECT source_row, referenced_row, comment_text, author, created_at_source
        FROM comments
        WHERE snapshot_id = ?
        ORDER BY source_row
        """,
        (snapshot_id,),
    ).fetchall()
    conn.close()
    return {"comments": _rows_to_list(rows)}


# ---------------------------------------------------------------------------
# POST /api/monthly-synthesis
# ---------------------------------------------------------------------------
@app.post("/api/monthly-synthesis")
def monthly_synthesis():
    """Trigger monthly executive PPTX generation and return the file path."""
    try:
        deck_path = run_synthesize(DB_PATH, f"{OUTPUT_DIR}/monthly")
    except Exception as exc:
        raise HTTPException(500, f"Monthly synthesis failed: {exc}") from exc
    return {"deck_path": deck_path}


# ---------------------------------------------------------------------------
# GET /api/files
# ---------------------------------------------------------------------------
@app.get("/api/files")
def download_file(path: str):
    """
    Stream a generated output file (weekly Markdown/JSON or monthly PPTX).
    The path must be inside the outputs/ directory to prevent path traversal.
    """
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(ALLOWED_OUTPUT_ROOT)
    except ValueError:
        raise HTTPException(403, "Access to this path is not allowed.")

    if not resolved.exists():
        raise HTTPException(404, f"File not found: {path}")

    suffix = resolved.suffix.lower()
    media_type_map = {
        ".md": "text/markdown",
        ".json": "application/json",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    return FileResponse(
        path=str(resolved),
        media_type=media_type_map.get(suffix, "application/octet-stream"),
        filename=resolved.name,
    )


# ---------------------------------------------------------------------------
# POST /api/ask
# ---------------------------------------------------------------------------
@app.post("/api/ask")
def ask(body: dict):
    """
    Simple natural-language query routed to the SQLite repository layer.
    Supports questions like: 'red projects', 'which projects have blockers?'
    """
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(400, "question is required")
    conn = _db()
    rows = simple_query(conn, question)
    conn.close()
    return {"rows": _rows_to_list(rows)}


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "db": DB_PATH}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _load_stored_weekly_json(json_path: str | None) -> dict:
    """
    Load the persisted weekly JSON report so we can serve the same
    reasons / recommendations / agent fields that were stored during analysis.

    The weekly JSON structure written by report_writer.py is:
      {
        "run_date": "...",
        "project": {"name": ..., "all_task_columns": [...]},
        "rag": {  <-- asdict(RagResult)
          "reasons": [...],
          "top_risks": [...],
          "recommendations": [...],
          "caveats": [...],
          "executive_summary": "...",
          "sentiment_summary": "...",
          "risk_themes": [...],
          "agent_mode": "..."
        }
      }
    We flatten the rag sub-key so callers can use e.g. stored.get('reasons').
    """
    if not json_path:
        return {}
    p = Path(json_path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    # Flatten: merge top-level with rag sub-dict, then add all_task_columns
    result: dict = {}
    rag_sub = data.get("rag", {})
    if isinstance(rag_sub, dict):
        result.update(rag_sub)
    project_sub = data.get("project", {})
    if isinstance(project_sub, dict):
        result["all_task_columns"] = project_sub.get("all_task_columns", [])
    return result


def _load_agent_fields_from_json(json_path: str | None) -> dict:
    """Extract agent-specific fields from a stored weekly JSON for the analyze response."""
    stored = _load_stored_weekly_json(json_path)
    return {
        "executive_summary": stored.get("executive_summary"),
        "sentiment_summary": stored.get("sentiment_summary"),
        "risk_themes": stored.get("risk_themes", []),
        "agent_mode": stored.get("agent_mode", "offline"),
    }
