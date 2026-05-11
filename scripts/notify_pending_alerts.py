from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.db.connection import get_connection
from app.db.repository import get_pending_alerts, mark_alerts_sent
from app.utils.logger import get_logger


logger = get_logger("notify_pending_alerts")
LOCAL_TIMEZONE = ZoneInfo("Europe/Warsaw")


def format_event_date(value: datetime) -> str:
    return value.astimezone(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M %Z")


def format_alert(alert: dict) -> str:
    location_parts = [
        value
        for value in (alert["venue_name"], alert["city"], alert["country_code"])
        if value
    ]
    location = ", ".join(location_parts) if location_parts else "unknown location"
    event_url = alert["event_url"] or "no event url"

    return (
        f"[#{alert['alert_id']}] {alert['artist_name']} | "
        f"{format_event_date(alert['event_date'])} | "
        f"{location} | match={alert['match_type']} | {event_url}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print pending concert alerts from the local database."
    )
    parser.add_argument(
        "--mark-sent",
        action="store_true",
        help="Mark printed alerts as sent.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conn = get_connection()

    try:
        alerts = get_pending_alerts(conn)

        if not alerts:
            print("No pending alerts.")
            return

        for alert in alerts:
            print(format_alert(alert))

        if args.mark_sent:
            alert_ids = [alert["alert_id"] for alert in alerts]
            marked = mark_alerts_sent(conn, alert_ids)
            logger.info("marked alerts as sent=%s", marked)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
