from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("config/rag_weights.json")


def load_rag_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return {
            "thresholds": {"green_max": 34, "amber_max": 69},
            "weights": {
                "schedule": 30,
                "progress": 20,
                "milestone": 20,
                "blockers": 15,
                "sentiment": 10,
                "budget": 5,
            },
            "blocker_keywords": ["blocked", "pending", "delay", "risk", "issue"],
            "negative_sentiment_keywords": ["pending", "delay", "risk", "blocked"],
            "positive_sentiment_keywords": ["completed", "done", "resolved"],
        }
    return json.loads(config_path.read_text(encoding="utf-8"))


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "project_name": ("Project Name",),
    "project_category": ("Project Category",),
    "ancestors": ("Ancestors",),
    "project_manager": ("Project Manager",),
    "level": ("Level",),
    "phase_milestone": ("Phase/Milestone",),
    "area": ("Area",),
    "at_risk": ("At Risk?", "At Risk"),
    "source_schedule_health": ("Schedule Health",),
    "task_name": ("Task Name",),
    "status": ("Status",),
    "percent_complete": ("% Complete", "Percent Complete"),
    "start_date": ("Start Date",),
    "end_date": ("End Date",),
    "baseline_start": ("Baseline Start",),
    "baseline_finish": ("Baseline Finish",),
    "baseline_start_date": ("Baseline Start Date",),
    "baseline_end_date": ("Baseline End Date",),
    "baseline_start2": ("Baseline Start2",),
    "baseline_finish2": ("Baseline Finish2",),
    "variance": ("Variance",),
    "variance2": ("Variance2",),
    "duration": ("Duration",),
    "total_float": ("Total Float",),
    "critical": ("Critical ?", "Critical?", "Critical"),
    "priority": ("Priority",),
    "owner": ("Owner",),
    "ownership": ("OwnerShip", "Ownership"),
    "assigned_to": ("Assigned To",),
    "predecessors": ("Predecessors",),
    "description": ("Description",),
    "status_comment": ("Status Comment",),
    "comments": ("Comments",),
    "on_hold": ("On Hold?", "On Hold"),
    "not_applicable": ("Not Applicable?", "Not Applicable"),
    "start": ("Start",),
    "finish": ("Finish",),
    "rag": ("RAG",),
    "days_until_today": ("No.of days Until Today", "No. of days Until Today"),
    "no_of_days": ("No.of days", "No. of days"),
    "target_start_to_today": ("Target start date to Today",),
}


EXPECTED_TASK_COLUMNS = sorted({alias for aliases in FIELD_ALIASES.values() for alias in aliases})
