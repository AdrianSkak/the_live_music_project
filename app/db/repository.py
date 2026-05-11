from __future__ import annotations

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.models import ParsedEvent, Source


def get_active_sources(conn) -> list[Source]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, artist_name, source_type, parser_key, source_url
            FROM sources
            WHERE is_active = TRUE
            ORDER BY id
            """
        )
        rows = cur.fetchall()

    return [
        Source(
            id=row["id"],
            artist_name=row["artist_name"],
            source_type=row["source_type"],
            parser_key=row["parser_key"],
            source_url=row["source_url"],
        )
        for row in rows
    ]


def create_scrape_run(conn, total_sources: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scrape_runs (total_sources)
            VALUES (%s)
            RETURNING id
            """,
            (total_sources,),
        )
        run_id = cur.fetchone()[0]

    conn.commit()
    return run_id


def finish_scrape_run(conn, run_id: int, succeeded: int, failed: int) -> None:
    if failed == 0:
        status = "success"
    elif succeeded > 0:
        status = "partial_success"
    else:
        status = "failed"

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE scrape_runs
            SET finished_at = NOW(),
                status = %s,
                succeeded_sources = %s,
                failed_sources = %s
            WHERE id = %s
            """,
            (status, succeeded, failed, run_id),
        )

    conn.commit()


def insert_raw_event(conn, scrape_run_id: int, source_id: int, event: ParsedEvent) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_events (
                scrape_run_id,
                source_id,
                artist_name,
                source_url,
                title,
                event_date_raw,
                event_date,
                city,
                venue,
                country,
                raw_payload,
                source_event_id,
                event_url
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                scrape_run_id,
                source_id,
                event.artist_name,
                event.source_url,
                event.title,
                event.event_date_raw,
                event.event_date,
                event.city,
                event.venue,
                event.country,
                Jsonb(event.raw_payload) if event.raw_payload else None,
                event.source_event_id,
                event.event_url,
            ),
        )

    conn.commit()


def insert_scrape_error(
    conn,
    scrape_run_id: int,
    source_id: int | None,
    stage: str,
    error_message: str,
    details: dict | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scrape_errors (
                scrape_run_id,
                source_id,
                stage,
                error_message,
                details
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                scrape_run_id,
                source_id,
                stage,
                error_message[:2000],
                Jsonb(details) if details else None,
            ),
        )

    conn.commit()


def process_raw_events(conn, scrape_run_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT process_raw_events(%s)", (scrape_run_id,))
        inserted_or_updated = cur.fetchone()[0]

    conn.commit()
    return inserted_or_updated


def get_pending_alerts(conn) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT
                a.id AS alert_id,
                a.match_type,
                a.status,
                e.id AS event_id,
                e.source,
                e.source_event_id,
                e.artist_name,
                e.venue_name,
                e.city,
                e.country_code,
                e.event_date,
                e.event_url,
                ta.artist_name AS tracked_artist_name,
                a.created_at AS alert_created_at
            FROM alerts a
            JOIN events e
                ON e.id = a.event_id
            JOIN tracked_artists ta
                ON ta.id = a.tracked_artist_id
            WHERE a.status = 'new'
            ORDER BY e.event_date ASC, a.id ASC
            """
        )
        return list(cur.fetchall())


def get_source_status(conn) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT
                id,
                artist_name,
                source_type,
                parser_key,
                source_url,
                is_active,
                created_at
            FROM sources
            ORDER BY id ASC
            """
        )
        return list(cur.fetchall())


def get_recent_scrape_runs(conn, limit: int = 5) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT
                id,
                status,
                total_sources,
                succeeded_sources,
                failed_sources,
                started_at,
                finished_at
            FROM scrape_runs
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,),
        )
        return list(cur.fetchall())


def get_pipeline_counts(conn) -> dict:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT
                (SELECT count(*) FROM sources) AS sources,
                (SELECT count(*) FROM sources WHERE is_active = TRUE) AS active_sources,
                (SELECT count(*) FROM raw_events) AS raw_events,
                (SELECT count(*) FROM events) AS events,
                (SELECT count(*) FROM alerts) AS alerts,
                (SELECT count(*) FROM alerts WHERE status = 'new') AS new_alerts,
                (SELECT count(*) FROM scrape_errors) AS scrape_errors
            """
        )
        return dict(cur.fetchone())


def mark_alerts_sent(conn, alert_ids: list[int]) -> int:
    if not alert_ids:
        return 0

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE alerts
            SET status = 'sent',
                sent_at = NOW(),
                error_message = NULL
            WHERE id = ANY(%s)
              AND status = 'new'
            """,
            (alert_ids,),
        )
        affected = cur.rowcount

    conn.commit()
    return affected
