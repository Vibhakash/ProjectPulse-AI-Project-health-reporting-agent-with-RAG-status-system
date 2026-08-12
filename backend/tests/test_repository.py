from datetime import date

from src.project_health.db import connect
from src.project_health.normalizer import load_project_workbook
from src.project_health.rag_engine import evaluate_rag
from src.project_health.reasoning import enrich_reasoning
from src.project_health.repositories import fetch_portfolio, save_analysis


def test_sqlite_persistence_roundtrip(tmp_path):
    sample = __import__("pathlib").Path.home() / "Downloads" / "S2P Project.xlsx"
    if not sample.exists():
        return

    conn = connect(tmp_path / "health.sqlite")
    workbook = load_project_workbook(sample)
    result = enrich_reasoning(workbook, evaluate_rag(workbook, date(2026, 7, 8)))
    snapshot_id = save_analysis(conn, workbook, result, {"json": "x.json", "markdown": "x.md"}, date(2026, 7, 8))

    assert snapshot_id > 0
    assert fetch_portfolio(conn)
    task_count = conn.execute("SELECT COUNT(*) AS c FROM tasks WHERE snapshot_id = ?", (snapshot_id,)).fetchone()["c"]
    signal_count = conn.execute("SELECT COUNT(*) AS c FROM rag_signals WHERE snapshot_id = ?", (snapshot_id,)).fetchone()["c"]
    assert task_count == len(workbook.tasks)
    assert signal_count == len(result.signals)
