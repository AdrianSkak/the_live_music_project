select
    a.id as alert_id,
    a.match_type,
    a.status,
    e.id as event_id,
    e.source,
    e.source_event_id,
    e.artist_name,
    e.venue_name,
    e.city,
    e.country_code,
    e.event_date,
    e.event_url,
    ta.artist_name as tracked_artist_name,
    a.created_at as alert_created_at
from alerts a
join events e
    on e.id = a.event_id
join tracked_artists ta
    on ta.id = a.tracked_artist_id
where a.status = 'new'
order by e.event_date asc, a.id asc;