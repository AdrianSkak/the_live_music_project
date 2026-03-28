create table if not exists events (
    id bigserial primary key,
    source text not null,
    source_event_id text not null,
    artist_name text not null,
    artist_name_normalized text not null,
    venue_name text,
    venue_name_normalized text,
    city text,
    city_normalized text,
    country_code text,
    event_date timestamptz not null,
    event_url text,
    raw_payload jsonb,
    created_at timestamptz not null default now(),

    constraint events_source_unique unique (source, source_event_id)
);

create table if not exists tracked_artists (
    id bigserial primary key,
    artist_name text not null,
    artist_name_normalized text not null,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),

    constraint tracked_artists_name_unique unique (artist_name_normalized)
);

create table if not exists tracked_cities (
    id bigserial primary key,
    city text not null,
    city_normalized text not null,
    country_code text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),

    constraint tracked_cities_unique unique (
        city_normalized, country_code
    )
);

create table if not exists tracked_venues (
    id bigserial primary key,
    venue_name text not null,
    venue_name_normalized text not null,
    city text,
    city_normalized text,
    country_code text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),

    constraint tracked_venues_unique unique (
        venue_name_normalized, city_normalized, country_code
)
);

create table if not exists alerts (
    id bigserial primary key,
    event_id bigint not null references events(id) on delete cascade,
    tracked_artist_id bigint not null references tracked_artists(id) on delete cascade,
    match_type text not null,
    status text not null default 'new',
    created_at timestamptz not null default now(),
    sent_at timestamptz,
    error_message text,

    constraint alerts_match_type_check
        check (match_type in ('city', 'venue', 'city_and_venue')),
    constraint alerts_status_check
        check (status in ('new', 'sent', 'failed')),
    constraint alerts_unique unique (event_id, tracked_artist_id, match_type)
);