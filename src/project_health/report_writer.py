from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from .metrics import project_metrics
from .schemas import ProjectWorkbook, RagResult


def write_weekly_reports(workbook: ProjectWorkbook, result: RagResult, output_dir: str | Path, run_date: date) -> dict[str, str]:
    weekly_dir = Path(output_dir) / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(workbook.detected_project_name)
    json_path = weekly_dir / f"{slug}_{run_date.isoformat()}.json"
    md_path = weekly_dir / f"{slug}_{run_date.isoformat()}.md"

    payload = _json_payload(workbook, result, run_date)
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    md_path.write_text(_markdown_report(workbook, result, payload["metrics"], run_date), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "project"


def _json_payload(workbook: ProjectWorkbook, result: RagResult, run_date: date) -> dict[str, Any]:
    return {
        "run_date": run_date.isoformat(),
        "project": {
            "name": workbook.detected_project_name,
            "source_file": workbook.source_file,
            "task_sheet": workbook.task_sheet,
            "summary": workbook.summary,
            "all_task_columns": workbook.all_task_columns,
        },
        "rag": asdict(result),
        "metrics": project_metrics(workbook, run_date),
        "data_quality_issues": [asdict(issue) for issue in workbook.data_quality_issues],
    }


def _markdown_report(workbook: ProjectWorkbook, result: RagResult, metrics: dict[str, Any], run_date: date) -> str:
    lines = [
        f"# Weekly Project Health Report: {workbook.detected_project_name}",
        "",
        f"Run date: {run_date.isoformat()}",
        f"Source file: `{Path(workbook.source_file).name}`",
        "",
        "## Executive Summary",
        "",
        f"- Agent RAG: **{result.status}**",
        f"- Risk score: **{result.score}/100**",
        f"- Confidence: **{result.confidence}**",
        f"- Data quality score: **{result.data_quality_score}%**",
        f"- Existing source schedule health: **{result.source_schedule_health or 'Unavailable'}**",
        f"- Agent mode: **{result.agent_mode}**",
    ]
    if result.rag_flip_alert:
        lines.append(f"- Alert: **{result.rag_flip_alert}**")
    lines.extend(["", "## Why This Status", ""])
    if result.executive_summary:
        lines.append(f"- {result.executive_summary}")
    lines.extend([f"- {reason}" for reason in result.reasons])
    lines.extend(["", "## Stakeholder Sentiment", ""])
    lines.append(result.sentiment_summary or "No stakeholder sentiment summary available.")
    lines.extend(["", "## Risk Themes", ""])
    lines.extend([f"- {theme}" for theme in (result.risk_themes or ["No repeated risk themes detected."])])

    lines.extend(["", "## Score Breakdown", ""])
    lines.append("| Signal | Weight | Score | Weighted | Evidence |")
    lines.append("|---|---:|---:|---:|---|")
    for signal in result.signals:
        score = "Excluded" if signal.score < 0 else f"{signal.score:.2f}"
        evidence = signal.evidence[0] if signal.evidence else ""
        lines.append(f"| {signal.name} | {signal.weight:.0f} | {score} | {signal.weighted_score:.1f} | {evidence} |")

    lines.extend(["", "## Delivery Indicators", ""])
    lines.append(f"- Tasks: {metrics['task_count']} total, {metrics['active_task_count']} active")
    lines.append(f"- Milestones/phases detected: {metrics['milestone_count']}")
    lines.append(f"- Average completion: {metrics['average_percent_complete']}%")
    lines.append(f"- Expected progress by dates: {metrics['expected_progress']}%")
    lines.append(f"- Progress gap: {metrics['progress_gap']} percentage points")
    lines.append(f"- Schedule health distribution: {metrics['health_counts']}")
    lines.append(f"- Status distribution: {metrics['status_counts']}")

    lines.extend(["", "## Top Risks", ""])
    lines.extend([f"- {risk}" for risk in result.top_risks])
    lines.extend(["", "## Recommended Actions", ""])
    lines.extend([f"- {rec}" for rec in result.recommendations])
    lines.extend(["", "## Data Caveats", ""])
    lines.extend([f"- {caveat}" for caveat in (result.caveats or ["No major caveats."])])
    lines.extend(["", "## Preserved Workbook Attributes", ""])
    lines.append(", ".join(f"`{col}`" for col in workbook.all_task_columns))
    lines.append("")
    return "\n".join(lines)
