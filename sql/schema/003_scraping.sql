CREATE TABLE sources (
    id BIGSERIAL PRIMARY KEY,
    artist_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT sources_source_type_check
        CHECK (source_type IN ('official_site', 'bandsintown', 'songkick', 'custom'))
);

CREATE TABLE scrape_runs (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running',
    total_sources INTEGER NOT NULL DEFAULT 0,
    succeeded_sources INTEGER NOT NULL DEFAULT 0,
    failed_sources INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT scrape_runs_status_check
        CHECK (status IN ('running', 'success', 'partial_success', 'failed'))
);

CREATE TABLE raw_events (
    id BIGSERIAL PRIMARY KEY,
    scrape_run_id BIGINT NOT NULL REFERENCES scrape_runs(id) ON DELETE CASCADE,
    source_id BIGINT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,

    artist_name TEXT NOT NULL,
    source_url TEXT NOT NULL,

    title TEXT,
    event_date_raw TEXT,
    event_date DATE,
    city TEXT,
    venue TEXT,
    country TEXT,

    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scrape_errors (
    id BIGSERIAL PRIMARY KEY,
    scrape_run_id BIGINT NOT NULL REFERENCES scrape_runs(id) ON DELETE CASCADE,
    source_id BIGINT REFERENCES sources(id) ON DELETE SET NULL,

    stage TEXT NOT NULL,
    error_message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT scrape_errors_stage_check
        CHECK (stage IN ('fetch', 'parse', 'save', 'process'))
);

CREATE INDEX idx_raw_events_scrape_run_id ON raw_events(scrape_run_id);
CREATE INDEX idx_raw_events_source_id ON raw_events(source_id);
CREATE INDEX idx_scrape_errors_scrape_run_id ON scrape_errors(scrape_run_id);
CREATE INDEX idx_scrape_errors_source_id ON scrape_errors(source_id);

CREATE OR REPLACE FUNCTION process_raw_events(p_scrape_run_id BIGINT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    inserted_count INTEGER := 0;
BEGIN
    INSERT INTO events (artist_name, event_date, city, venue, source_url)
    SELECT
        re.artist_name,
        re.event_date,
        re.city,
        re.venue,
        re.source_url
    FROM raw_events re
    WHERE re.scrape_run_id = p_scrape_run_id
      AND re.event_date IS NOT NULL
      AND re.city IS NOT NULL
      AND re.venue IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM events e
          WHERE e.artist_name = re.artist_name
            AND e.event_date = re.event_date
            AND e.city = re.city
            AND e.venue = re.venue
      );

    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RETURN inserted_count;
END;
$$;