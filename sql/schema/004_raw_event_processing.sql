CREATE EXTENSION IF NOT EXISTS unaccent;

ALTER TABLE raw_events
    ALTER COLUMN event_date TYPE TIMESTAMPTZ
    USING CASE
        WHEN event_date IS NULL THEN NULL
        ELSE event_date::timestamptz
    END;

ALTER TABLE raw_events
    ADD COLUMN IF NOT EXISTS source_event_id TEXT,
    ADD COLUMN IF NOT EXISTS event_url TEXT;

CREATE OR REPLACE FUNCTION normalize_text(p_value TEXT)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT NULLIF(
        regexp_replace(
            lower(trim(unaccent(COALESCE(p_value, '')))),
            '\s+',
            ' ',
            'g'
        ),
        ''
    );
$$;

CREATE OR REPLACE FUNCTION process_raw_events(p_scrape_run_id BIGINT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected_count INTEGER := 0;
BEGIN
    INSERT INTO events (
        source,
        source_event_id,
        artist_name,
        artist_name_normalized,
        venue_name,
        venue_name_normalized,
        city,
        city_normalized,
        country_code,
        event_date,
        event_url,
        raw_payload
    )
    SELECT
        COALESCE(s.source_type, 'custom') AS source,
        COALESCE(
            re.source_event_id,
            md5(
                concat_ws(
                    '|',
                    s.id::text,
                    COALESCE(re.artist_name, ''),
                    COALESCE(re.event_date::text, ''),
                    COALESCE(re.venue, ''),
                    COALESCE(re.city, ''),
                    COALESCE(re.event_url, re.source_url, '')
                )
            )
        ) AS source_event_id,
        re.artist_name,
        normalize_text(re.artist_name) AS artist_name_normalized,
        re.venue AS venue_name,
        normalize_text(re.venue) AS venue_name_normalized,
        re.city,
        normalize_text(re.city) AS city_normalized,
        UPPER(NULLIF(re.country, '')) AS country_code,
        re.event_date,
        COALESCE(re.event_url, re.source_url) AS event_url,
        COALESCE(
            re.raw_payload,
            jsonb_build_object(
                'title', re.title,
                'event_date_raw', re.event_date_raw,
                'source_url', re.source_url
            )
        ) AS raw_payload
    FROM raw_events re
    JOIN sources s ON s.id = re.source_id
    WHERE re.scrape_run_id = p_scrape_run_id
      AND re.artist_name IS NOT NULL
      AND re.event_date IS NOT NULL
    ON CONFLICT (source, source_event_id) DO UPDATE
    SET artist_name = EXCLUDED.artist_name,
        artist_name_normalized = EXCLUDED.artist_name_normalized,
        venue_name = EXCLUDED.venue_name,
        venue_name_normalized = EXCLUDED.venue_name_normalized,
        city = EXCLUDED.city,
        city_normalized = EXCLUDED.city_normalized,
        country_code = EXCLUDED.country_code,
        event_date = EXCLUDED.event_date,
        event_url = EXCLUDED.event_url,
        raw_payload = EXCLUDED.raw_payload;

    GET DIAGNOSTICS v_affected_count = ROW_COUNT;
    RETURN v_affected_count;
END;
$$;