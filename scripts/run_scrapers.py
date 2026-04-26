from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.db.connection import get_connection
from app.db.repository import (
    create_scrape_run,
    finish_scrape_run,
    get_active_sources,
    insert_raw_event,
    insert_scrape_error,
    process_raw_events,
)
from app.services.fetcher import fetch_html
from app.services.source_parsers.registry import get_parser
from app.utils.logger import get_logger


logger = get_logger("run_scrapers")


def main() -> None:
    conn = get_connection()

    try:
        sources = get_active_sources(conn)
        run_id = create_scrape_run(conn, total_sources=len(sources))

        logger.info("scrape_run_id=%s, sources=%s", run_id, len(sources))

        succeeded = 0
        failed = 0

        for source in sources:
            logger.info("start source id=%s artist=%s", source.id, source.artist_name)

            try:
                parser = get_parser(source.parser_key)
                html, final_url = fetch_html(source.source_url)
                events = parser.parse(html, source)

                for event in events:
                    event.source_url = final_url
                    insert_raw_event(conn, run_id, source.id, event)

                logger.info(
                    "source ok id=%s artist=%s events=%s",
                    source.id,
                    source.artist_name,
                    len(events),
                )
                succeeded += 1

            except Exception as exc:
                failed += 1
                logger.exception("source failed id=%s artist=%s", source.id, source.artist_name)

                insert_scrape_error(
                    conn=conn,
                    scrape_run_id=run_id,
                    source_id=source.id,
                    stage="parse",
                    error_message=str(exc),
                    details={
                        "artist_name": source.artist_name,
                        "source_url": source.source_url,
                        "parser_key": source.parser_key,
                    },
                )

        try:
            affected = process_raw_events(conn, run_id)
            logger.info("process_raw_events affected=%s", affected)
        except Exception as exc:
            logger.exception("process_raw_events failed")
            insert_scrape_error(
                conn=conn,
                scrape_run_id=run_id,
                source_id=None,
                stage="process",
                error_message=str(exc),
                details={},
            )

        finish_scrape_run(conn, run_id, succeeded=succeeded, failed=failed)
        logger.info("run finished succeeded=%s failed=%s", succeeded, failed)

    finally:
        conn.close()


if __name__ == "__main__":
    main()