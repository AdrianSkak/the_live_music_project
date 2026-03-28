insert into tracked_artists (artist_name, artist_name_normalized)
values
    ('Metallica', 'metallica'),
    ('Opeth', 'opeth')
on conflict (artist_name_normalized) do nothing;

insert into tracked_cities (city, city_normalized, country_code)
values
    ('Warszawa', 'warszawa', 'PL'),
    ('Kraków', 'krakow', 'PL')
on conflict do nothing;

insert into tracked_venues (venue_name, venue_name_normalized, city, city_normalized, country_code)
values
    ('Progresja', 'progresja', 'Warszawa', 'warszawa', 'PL'),
    ('Tauron Arena Kraków', 'tauron arena krakow', 'Kraków', 'krakow', 'PL')
on conflict do nothing;

insert into events (
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
values
    (
        'manual_test',
        'evt_001',
        'Metallica',
        'metallica',
        'Progresja',
        'progresja',
        'Warszawa',
        'warszawa',
        'PL',
        '2026-11-15 19:00:00+01',
        'https://example.com/metallica-warszawa',
        '{"note": "test event"}'::jsonb
    ),
    (
        'manual_test',
        'evt_002',
        'Opeth',
        'opeth',
        'Tauron Arena Kraków',
        'tauron arena krakow',
        'Kraków',
        'krakow',
        'PL',
        '2026-12-01 20:00:00+01',
        'https://example.com/opeth-krakow',
        '{"note": "test event"}'::jsonb
    ),
    (
        'manual_test',
        'evt_003',
        'Metallica',
        'metallica',
        'PGE Narodowy',
        'pge narodowy',
        'Warszawa',
        'warszawa',
        'PL',
        '2026-11-20 19:00:00+01',
        null,
        '{"note": "city only test"}'::jsonb
    ),
    (
        'manual_test',
        'evt_004',
        'Metallica',
        'metallica',
        'Spodek',
        'spodek',
        'Katowice',
        'katowice',
        'PL',
        '2026-11-25 19:00:00+01',
        null,
        '{"note": "no match test"}'::jsonb
    )
on conflict (source, source_event_id) do nothing;