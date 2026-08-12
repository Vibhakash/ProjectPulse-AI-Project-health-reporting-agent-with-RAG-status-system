from pathlib import Path

from src.project_health.normalizer import load_project_workbook
from src.project_health.rag_engine import evaluate_rag


def test_rag_engine_returns_auditable_signals():
    sample = Path.home() / "Downloads" / "Project Plan B.xlsx"
    if not sample.exists():
        return

    workbook = load_project_workbook(sample)
    result = evaluate_rag(workbook)

    assert result.status in {"Green", "Amber", "Red"}
    assert result.signals
    assert any(signal.name == "budget" and signal.score < 0 for signal in result.signals)
    assert result.data_quality_score > 0
