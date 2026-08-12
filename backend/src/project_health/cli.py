from __future__ import annotations

import argparse
import shutil
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from .db import connect
from .monthly_synthesis import generate_monthly_deck
from .normalizer import load_project_workbook
from .rag_engine import evaluate_rag
from .reasoning import enrich_reasoning
from .report_writer import write_weekly_reports
from .repositories import save_analysis, simple_query
from .alert_service import send_rag_flip_alert


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Project Health Reporting Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze project plans and generate weekly reports")
    analyze.add_argument("--input", required=True, help="Input folder containing .xlsx project plans")
    analyze.add_argument("--output", default="outputs", help="Output folder")
    analyze.add_argument("--db", default="storage/project_health.sqlite", help="SQLite database path")
    analyze.add_argument("--config", default=None, help="Optional RAG config JSON path")
    analyze.add_argument("--run-date", default=None, help="Run date in YYYY-MM-DD format")
    analyze.add_argument("--copy-samples", action="store_true", help="Copy provided sample files from Downloads into input folder if present")

    synth = sub.add_parser("synthesize", help="Generate monthly executive deck")
    synth.add_argument("--db", default="storage/project_health.sqlite", help="SQLite database path")
    synth.add_argument("--output", default="outputs/monthly", help="Monthly output folder")

    ask = sub.add_parser("ask", help="Simple natural-language query over SQLite")
    ask.add_argument("question")
    ask.add_argument("--db", default="storage/project_health.sqlite", help="SQLite database path")

    schedule = sub.add_parser("schedule", help="Run the agent weekly in a simple local loop")
    schedule.add_argument("--input", required=True)
    schedule.add_argument("--output", default="outputs")
    schedule.add_argument("--db", default="storage/project_health.sqlite")
    schedule.add_argument("--interval-seconds", type=int, default=604800)

    args = parser.parse_args()
    if args.command == "analyze":
        run_analyze(args.input, args.output, args.db, args.config, _parse_date(args.run_date), args.copy_samples)
    elif args.command == "synthesize":
        run_synthesize(args.db, args.output)
    elif args.command == "ask":
        run_ask(args.db, args.question)
    elif args.command == "schedule":
        run_schedule(args.input, args.output, args.db, args.interval_seconds)


def run_analyze(input_dir: str, output_dir: str, db_path: str, config_path: str | None, run_date: date, copy_samples: bool = False) -> list[int]:
    load_dotenv()
    input_path = Path(input_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    if copy_samples:
        _copy_samples(input_path)
    files = sorted(input_path.glob("*.xlsx"))
    if not files:
        raise ValueError(f"No .xlsx files found in {input_path}")

    conn = connect(db_path)
    snapshot_ids = []
    seen_project_names: dict[str, int] = {}  # Track duplicates within same batch
    for file in files:
        try:
            workbook = load_project_workbook(file, run_date)
        except Exception as exc:
            print(f"SKIP {file.name}: {exc}")
            continue
        # We intentionally keep the same project_name across multiple files
        # so that they map to the exact same `project_id` for Trend chart rendering.
        result = enrich_reasoning(workbook, evaluate_rag(workbook, run_date, config_path))
        output_paths = write_weekly_reports(workbook, result, output_dir, run_date)
        snapshot_id = save_analysis(conn, workbook, result, output_paths, run_date)
        snapshot_ids.append(snapshot_id)
        print(f"{workbook.detected_project_name}: {result.status} ({result.score}/100) -> {output_paths['markdown']}")
        # Send email alert if RAG status flipped
        if result.rag_flip_alert:
            parts = result.rag_flip_alert.split("->")
            if len(parts) == 2:
                old_s = parts[0].strip().split()[-1]
                new_s = parts[1].strip().split()[0]
                send_rag_flip_alert(
                    project_name=workbook.detected_project_name,
                    old_status=old_s,
                    new_status=new_s,
                    run_date=run_date.isoformat(),
                )
    conn.close()
    return snapshot_ids


def run_synthesize(db_path: str, output_dir: str) -> str:
    load_dotenv()
    conn = connect(db_path)
    deck_path = generate_monthly_deck(conn, output_dir)
    conn.close()
    print(f"Monthly synthesis generated: {deck_path}")
    return deck_path


def run_ask(db_path: str, question: str) -> None:
    conn = connect(db_path)
    rows = simple_query(conn, question)
    if not rows:
        print("No matching rows found.")
    for row in rows:
        print(dict(row))
    conn.close()


def run_schedule(input_dir: str, output_dir: str, db_path: str, interval_seconds: int) -> None:
    print(f"Starting weekly scheduler loop. Interval seconds: {interval_seconds}")
    while True:
        run_analyze(input_dir, output_dir, db_path, None, date.today())
        run_synthesize(db_path, str(Path(output_dir) / "monthly"))
        time.sleep(interval_seconds)


def _copy_samples(input_path: Path) -> None:
    downloads = Path.home() / "Downloads"
    for name in ("S2P Project.xlsx", "Project Plan B.xlsx"):
        source = downloads / name
        if source.exists():
            shutil.copy2(source, input_path / name)


def _parse_date(value: str | None) -> date:
    return date.fromisoformat(value) if value else date.today()


if __name__ == "__main__":
    main()
