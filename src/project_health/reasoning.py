from __future__ import annotations

from .agent import ProjectHealthAgent
from .schemas import ProjectWorkbook, RagResult


def enrich_reasoning(workbook: ProjectWorkbook, result: RagResult) -> RagResult:
    """Enrich deterministic RAG output with the Project Health Agent.

    The deterministic rule engine remains the source of truth for the RAG
    color and score. The agent summarizes evidence, stakeholder sentiment,
    risk themes, and recommendations.
    """
    return ProjectHealthAgent().enrich(workbook, result)
