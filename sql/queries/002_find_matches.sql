select
    e.id as event_id,
    e.source,
    e.source_event_id,
    e.artist_name,
    e.venue_name,
    e.city,
    e.event_date,
    ta.id as tracked_artist_id,
    ta.artist_name as tracked_artist_name,
    tc.id as tracked_city_id,
    tv.id as tracked_venue_id,
    case
        when tc.id is not null and tv.id is not null then 'city_and_venue'
        when tv.id is not null then 'venue'
        when tc.id is not null then 'city'
        else null
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
order by e.id;