create or replace function generate_alerts()
returns integer
language plpgsql
as $$
declare
    v_inserted_count integer;
begin
    insert into alerts (
        event_id,
        tracked_artist_id,
        match_type
    )
    select
        e.id as event_id,
        ta.id as tracked_artist_id,
        case
            when tc.id is not null and tv.id is not null then 'city_and_venue'
            when tv.id is not null then 'venue'
            when tc.id is not null then 'city'
        end as match_type
    from events e
    join tracked_artists ta
        on ta.artist_name_normalized = e.artist_name_normalized
       and ta.is_active = true
    left join tracked_cities tc
        on tc.city_normalized = e.city_normalized
       and tc.is_active = true
       and (tc.country_code is null or tc.country_code = e.country_code)
    left join tracked_venues tv
        on tv.venue_name_normalized = e.venue_name_normalized
       and tv.is_active = true
       and (tv.city_normalized is null or tv.city_normalized = e.city_normalized)
       and (tv.country_code is null or tv.country_code = e.country_code)
    where tc.id is not null
       or tv.id is not null
    on conflict (event_id, tracked_artist_id, match_type) do nothing;

    get diagnostics v_inserted_count = row_count;

    return v_inserted_count;
end;
$$;