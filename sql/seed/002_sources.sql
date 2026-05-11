INSERT INTO sources (artist_name, source_type, source_url, parser_key, is_active)
VALUES
    (
        'Metallica',
        'official_site',
        'https://www.metallica.com/tour',
        'metallica_tour',
        TRUE
    ),
    (
        'Iron Maiden',
        'official_site',
        'https://www.ironmaiden.com/tour/run-for-your-lives-world-tour-2026/',
        'iron_maiden_tour_2026',
        TRUE
    ),
    (
        'Rammstein',
        'official_site',
        'https://www.rammstein.de/en/live/',
        'rammstein_live',
        FALSE
    )
ON CONFLICT (source_url) DO UPDATE
SET artist_name = EXCLUDED.artist_name,
    source_type = EXCLUDED.source_type,
    parser_key = EXCLUDED.parser_key,
    is_active = EXCLUDED.is_active;
