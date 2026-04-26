ALTER TABLE sources
    ADD COLUMN IF NOT EXISTS parser_key TEXT;

UPDATE sources
SET parser_key = CASE
    WHEN artist_name = 'Metallica' THEN 'metallica_tour'
    WHEN artist_name = 'Iron Maiden' THEN 'iron_maiden_tour_2026'
    WHEN artist_name = 'Rammstein' THEN 'rammstein_live'
    ELSE 'custom'
END
WHERE parser_key IS NULL;

UPDATE sources
SET source_url = 'https://www.ironmaiden.com/tour/run-for-your-lives-world-tour-2026/'
WHERE artist_name = 'Iron Maiden';

ALTER TABLE sources
    ALTER COLUMN parser_key SET NOT NULL;

ALTER TABLE sources
    ADD CONSTRAINT sources_parser_key_not_blank
    CHECK (length(trim(parser_key)) > 0);