from pathlib import Path

from src.project_health.normalizer import load_project_workbook


def test_normalizer_preserves_all_known_columns_from_plan_b():
    sample = Path.home() / "Downloads" / "Project Plan B.xlsx"
    if not sample.exists():
        return

    workbook = load_project_workbook(sample)

    assert "Baseline Start2" in workbook.all_task_columns
    assert "Baseline Finish2" in workbook.all_task_columns
    assert "Variance2" in workbook.all_task_columns
    assert workbook.tasks
    assert workbook.tasks[0].raw_data


def test_comments_sheet_keeps_first_comment_row():
    sample = Path.home() / "Downloads" / "S2P Project.xlsx"
    if not sample.exists():
        return

    workbook = load_project_workbook(sample)

    assert workbook.comments
    assert "scheduled agenda" in workbook.comments[0].comment_text.lower()
