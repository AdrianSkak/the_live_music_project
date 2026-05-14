from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.db.connection import get_connection
from app.db.repository import get_pending_alerts, mark_alerts_sent
from app.services.notifications.alert_formatter import (
    format_alert_email_body,
    format_alert_email_subject,
)
from app.services.notifications.email_notifier import EmailConfig, send_email
from app.utils.logger import get_logger


logger = get_logger("send_pending_alert_emails")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or send pending concert alerts by email."
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send the email. Without this flag, only print a preview.",
    )
    parser.add_argument(
        "--mark-sent",
        action="store_true",
        help="Mark alerts as sent after a successful email send.",
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

        subject = format_alert_email_subject(alerts)
        body = format_alert_email_body(alerts)

        if not args.send:
            print(f"Subject: {subject}")
            print()
            print(body)
            print()
            print("Preview only. Use --send to send this email.")
            return

        config = EmailConfig.from_env()
        send_email(config, subject, body)
        logger.info("sent email alerts=%s recipients=%s", len(alerts), len(config.recipients))

        if args.mark_sent:
            alert_ids = [alert["alert_id"] for alert in alerts]
            marked = mark_alerts_sent(conn, alert_ids)
            logger.info("marked alerts as sent=%s", marked)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
