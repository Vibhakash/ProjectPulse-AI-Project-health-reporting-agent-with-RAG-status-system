from __future__ import annotations

from collections import Counter
from datetime import date

from .config import load_rag_config
from .metrics import data_quality_score, project_metrics, source_project_health
from .schemas import ProjectWorkbook, RagResult, RagSignal


def evaluate_rag(workbook: ProjectWorkbook, as_of: date | None = None, config_path: str | None = None) -> RagResult:
    config = load_rag_config(config_path)
    weights = config["weights"]
    metrics = project_metrics(workbook, as_of)

    signals = [
        _schedule_signal(workbook, metrics, weights["schedule"]),
        _progress_signal(metrics, weights["progress"]),
        _milestone_signal(workbook, weights["milestone"]),
        _blocker_signal(workbook, config, weights["blockers"]),
        _sentiment_signal(workbook, config, weights["sentiment"]),
        _budget_signal(workbook, weights["budget"]),
    ]

    available = [s for s in signals if s.score >= 0]
    total_weight = sum(signal.weight for signal in available) or 1
    score = round(sum(signal.weighted_score for signal in available) / total_weight * 100, 1)

    thresholds = config["thresholds"]
    status = "Green" if score <= thresholds["green_max"] else "Amber" if score <= thresholds["amber_max"] else "Red"
    if any(signal.triggered_override for signal in signals):
        status = "Red"

    dq_score = data_quality_score(workbook)
    confidence = "High" if dq_score >= 80 else "Medium" if dq_score >= 55 else "Low"
    source_health = source_project_health(workbook)

    return RagResult(
        project_name=workbook.detected_project_name,
        status=status,
        score=score,
        confidence=confidence,
        data_quality_score=dq_score,
        source_schedule_health=source_health,
        signals=signals,
        reasons=_reasons(status, signals, metrics, source_health),
        top_risks=_top_risks(workbook, metrics),
        recommendations=_recommendations(status, signals),
        caveats=_caveats(workbook, signals),
    )


def _schedule_signal(workbook: ProjectWorkbook, metrics: dict, weight: float) -> RagSignal:
    counts = Counter((task.source_schedule_health or "").strip().lower() for task in workbook.tasks)
    total = max(1, sum(counts.values()))
    red = counts.get("red", 0)
    amber = counts.get("yellow", 0) + counts.get("amber", 0)
    late = len(metrics["late_tasks"])
    score = min(1, (red / total * 1.8) + (amber / total * 0.8) + min(late, 10) / 20)
    project_health = (metrics["red_or_yellow_tasks"][0]["health"] if metrics["red_or_yellow_tasks"] else None)
    override = red > 0 and (workbook.summary.get("At Risk") == "High" or _root_health(workbook) == "red")
    evidence = [f"{red} red and {amber} amber/yellow schedule-health rows", f"{late} active tasks appear late"]
    if project_health:
        evidence.append(f"Example at-risk row health: {project_health}")
    return RagSignal("schedule", weight, f"red={red}, amber_or_yellow={amber}, late={late}", round(score, 3), round(score * weight, 3), evidence, override)


def _progress_signal(metrics: dict, weight: float) -> RagSignal:
    gap = metrics.get("progress_gap")
    if gap is None:
        return RagSignal("progress", weight, "expected progress unavailable", -1, 0, ["Missing or incomplete project dates."])
    if gap <= 5:
        score = 0.1
    elif gap <= 15:
        score = 0.45
    elif gap <= 25:
        score = 0.7
    else:
        score = 1
    return RagSignal(
        "progress",
        weight,
        f"expected={metrics['expected_progress']}%, actual={metrics['average_percent_complete']}%, gap={gap}%",
        score,
        round(score * weight, 3),
        [f"Completion is {abs(gap):.1f} points {'behind' if gap > 0 else 'ahead of'} expected timeline."],
        gap > 30,
    )


def _milestone_signal(workbook: ProjectWorkbook, weight: float) -> RagSignal:
    milestones = [task for task in workbook.tasks if task.phase_milestone or (task.level is not None and task.level <= 1)]
    if not milestones:
        return RagSignal("milestone", weight, "no milestone rows detected", -1, 0, ["No milestone/phase rows detected."])
    risky = [
        task for task in milestones
        if (task.source_schedule_health or "").lower() in {"red", "yellow", "amber"}
        or ((task.status or "").lower() != "completed" and task.percent_complete is not None and task.percent_complete < 80)
    ]
    score = min(1, len(risky) / max(1, len(milestones)))
    evidence = [f"{len(risky)} of {len(milestones)} phase/milestone rows show schedule or completion risk."]
    evidence.extend([f"Row {task.source_row}: {task.task_name}" for task in risky[:3] if task.task_name])
    return RagSignal("milestone", weight, f"risky={len(risky)}, total={len(milestones)}", round(score, 3), round(score * weight, 3), evidence, score > 0.65)


def _blocker_signal(workbook: ProjectWorkbook, config: dict, weight: float) -> RagSignal:
    keywords = [word.lower() for word in config.get("blocker_keywords", [])]
    blockers = []
    for task in workbook.tasks:
        text = " ".join([task.status_comment or "", task.comments or "", task.task_name or ""]).lower()
        completed = (task.status or "").strip().lower() in {"completed", "complete"}
        active_critical = task.critical and not completed
        if active_critical or task.on_hold or (task.total_float is not None and task.total_float < 0) or any(word in text for word in keywords):
            blockers.append(task)
    score = min(1, len(blockers) / max(5, len(workbook.tasks) * 0.08))
    evidence = [f"{len(blockers)} task rows show blocker, critical-path, on-hold, negative-float, or keyword risk."]
    evidence.extend([f"Row {task.source_row}: {task.task_name}" for task in blockers[:3] if task.task_name])
    return RagSignal("blockers", weight, f"blocker_rows={len(blockers)}", round(score, 3), round(score * weight, 3), evidence, len(blockers) >= 8)


def _sentiment_signal(workbook: ProjectWorkbook, config: dict, weight: float) -> RagSignal:
    if not workbook.comments:
        return RagSignal("sentiment", weight, "no comments", -1, 0, ["No stakeholder sentiment data available."])
    negative = config.get("negative_sentiment_keywords", [])
    positive = config.get("positive_sentiment_keywords", [])
    neg_count = 0
    pos_count = 0
    evidence = []
    for comment in workbook.comments:
        text = comment.comment_text.lower()
        if any(word in text for word in negative):
            neg_count += 1
            if len(evidence) < 3:
                evidence.append(f"Comment row {comment.source_row}: {comment.comment_text[:140]}")
        if any(word in text for word in positive):
            pos_count += 1
    score = min(1, max(0, (neg_count - pos_count * 0.4) / max(1, len(workbook.comments))))
    if not evidence:
        evidence.append("Comments do not show repeated blocker language.")
    return RagSignal("sentiment", weight, f"negative={neg_count}, positive={pos_count}, total={len(workbook.comments)}", round(score, 3), round(score * weight, 3), evidence, score > 0.7 and neg_count >= 5)


def _budget_signal(workbook: ProjectWorkbook, weight: float) -> RagSignal:
    budget_columns = [col for col in workbook.all_task_columns if any(term in col.lower() for term in ["budget", "cost", "burn", "actual spend"])]
    if not budget_columns:
        return RagSignal("budget", weight, "budget fields unavailable", -1, 0, ["Budget/burn columns are absent in the provided workbook."])
    return RagSignal("budget", weight, f"budget_columns={budget_columns}", 0.2, round(0.2 * weight, 3), ["Budget fields exist but require project-specific variance mapping."])


def _root_health(workbook: ProjectWorkbook) -> str | None:
    for task in workbook.tasks:
        if task.level in (0, None) and task.source_schedule_health:
            return task.source_schedule_health.lower()
    return None


def _reasons(status: str, signals: list[RagSignal], metrics: dict, source_health: str | None) -> list[str]:
    ordered = sorted([s for s in signals if s.score >= 0], key=lambda s: s.weighted_score, reverse=True)
    reasons = [f"Agent-derived status is {status} with a risk score of {round(sum(s.weighted_score for s in ordered), 1)} weighted points before normalization."]
    if source_health:
        reasons.append(f"Existing source schedule health is {source_health}; the agent uses it only as evidence, not as the final decision.")
    for signal in ordered[:3]:
        reasons.append(f"{signal.name.title()} contributed {signal.weighted_score:.1f} weighted points: {signal.evidence[0]}")
    if metrics.get("progress_gap") is not None:
        reasons.append(f"Average completion is {metrics['average_percent_complete']}% versus expected progress of {metrics['expected_progress']}%.")
    return reasons


def _top_risks(workbook: ProjectWorkbook, metrics: dict) -> list[str]:
    risks = []
    for key in ("critical_negative_float_tasks", "red_or_yellow_tasks", "blocker_text_tasks", "late_tasks"):
        for item in metrics.get(key, [])[:3]:
            risks.append(f"Row {item['row']}: {item['task']} ({item.get('health') or item.get('status') or 'risk signal'})")
            if len(risks) >= 6:
                return risks
    if not risks:
        risks.append("No major task-level risk stood out from available data.")
    return risks


def _recommendations(status: str, signals: list[RagSignal]) -> list[str]:
    recs = []
    risky = {signal.name for signal in signals if signal.score >= 0.45 or signal.triggered_override}
    if "schedule" in risky:
        recs.append("Run a schedule recovery review focused on red/yellow rows and near-term milestones.")
    if "milestone" in risky:
        recs.append("Ask the PM to confirm owners and dates for at-risk phase/milestone rows.")
    if "blockers" in risky:
        recs.append("Create an escalation list for critical-path, pending, and dependency-driven blockers.")
    if "sentiment" in risky:
        recs.append("Summarize open stakeholder asks and close the loop with owners before the next weekly review.")
    if status == "Green":
        recs.append("Maintain current cadence and monitor for RAG movement in the next weekly snapshot.")
    return recs[:5]


def _caveats(workbook: ProjectWorkbook, signals: list[RagSignal]) -> list[str]:
    caveats = [signal.evidence[0] for signal in signals if signal.score < 0]
    caveats.extend(issue.message for issue in workbook.data_quality_issues[:5])
    return list(dict.fromkeys(caveats))[:6]
