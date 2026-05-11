from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.db.connection import get_connection
from app.db.repository import (
    get_pipeline_counts,
    get_recent_scrape_runs,
    get_source_status,
)


LOCAL_TIMEZONE = ZoneInfo("Europe/Warsaw")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.astimezone(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S %Z")


def print_counts(counts: dict) -> None:
    print("Pipeline counts")
    print(f"- sources: {counts['sources']} ({counts['active_sources']} active)")
    print(f"- raw_events: {counts['raw_events']}")
    print(f"- events: {counts['events']}")
    print(f"- alerts: {counts['alerts']} ({counts['new_alerts']} new)")
    print(f"- scrape_errors: {counts['scrape_errors']}")


def print_sources(sources: list[dict]) -> None:
    print()
    print("Sources")
    if not sources:
        print("- none")
        return

    for source in sources:
        active_marker = "active" if source["is_active"] else "inactive"
        print(
            f"- #{source['id']} {source['artist_name']} | "
            f"{source['parser_key']} | {active_marker} | {source['source_url']}"
        )


def print_scrape_runs(scrape_runs: list[dict]) -> None:
    print()
    print("Recent scrape runs")
    if not scrape_runs:
        print("- none")
        return

    for run in scrape_runs:
        print(
            f"- #{run['id']} {run['status']} | "
            f"sources={run['total_sources']} "
            f"ok={run['succeeded_sources']} "
            f"failed={run['failed_sources']} | "
            f"started={format_datetime(run['started_at'])} | "
            f"finished={format_datetime(run['finished_at'])}"
        )


def main() -> None:
    conn = get_connection()

    try:
        print_counts(get_pipeline_counts(conn))
        print_sources(get_source_status(conn))
        print_scrape_runs(get_recent_scrape_runs(conn))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
