# The Live Music Project

MVP aplikacji do wykrywania koncertow obserwowanych artystow w wybranych
lokalizacjach.

Projekt jest obecnie w fazie database-first:

- PostgreSQL przechowuje zrodla, raw eventy, przetworzone wydarzenia i alerty.
- Python pobiera HTML, wybiera parser po `parser_key` i zapisuje raw eventy.
- Logika przetwarzania raw eventow i generowania alertow mieszka w SQL.

## Wymagania

- Docker Compose
- Python 3.11+

Zainstaluj zaleznosci:

```powershell
python -m pip install -r requirements.txt
```

## Baza danych

Uruchom PostgreSQL:

```powershell
docker compose up -d
```

Domyslny connection string:

```text
postgresql://postgres:postgres@localhost:5432/live_music
```

Mozesz go nadpisac przez `DATABASE_URL`.

W PowerShellu:

```powershell
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/live_music"
```

## Schemat i dane testowe

Pliki SQL sa w katalogach:

- `sql/schema` - schemat, funkcje i migracje
- `sql/seed` - dane startowe
- `sql/queries` - zapytania pomocnicze

Uruchamiaj schematy w kolejnosci numerycznej, a potem seedy:

```powershell
psql $env:DATABASE_URL -f sql/schema/001_init.sql
psql $env:DATABASE_URL -f sql/schema/002_alert_functions.sql
psql $env:DATABASE_URL -f sql/schema/003_scraping.sql
psql $env:DATABASE_URL -f sql/schema/004_raw_event_processing.sql
psql $env:DATABASE_URL -f sql/schema/005_parser_keys.sql
psql $env:DATABASE_URL -f sql/schema/006_deactivate_unsupported_sources.sql
psql $env:DATABASE_URL -f sql/seed/001_test_data.sql
psql $env:DATABASE_URL -f sql/seed/002_sources.sql
```

## Scrapery

Glowne wejscie:

```powershell
python scripts/run_scrapers.py
```

Runner:

1. pobiera aktywne zrodla z tabeli `sources`,
2. wybiera parser przez `parser_key`,
3. pobiera HTML,
4. zapisuje rekordy do `raw_events`,
5. odpala `process_raw_events(scrape_run_id)`.

Obecnie aktywne parsery:

- `metallica_tour`
- `iron_maiden_tour_2026`

Rammstein jest w seedzie jako nieaktywny, dopoki nie ma parsera
`rammstein_live`.

Sprawdz status pipeline'u bez modyfikowania bazy:

```powershell
python scripts/check_pipeline_status.py
```

## Alerty

Wygeneruj alerty:

```sql
select generate_alerts();
```

Podejrzyj nowe alerty:

```powershell
psql $env:DATABASE_URL -f sql/queries/001_pending_alerts.sql
```

Wypisz alerty w konsoli:

```powershell
python scripts/notify_pending_alerts.py
```

Wypisz alerty i oznacz je jako wyslane:

```powershell
python scripts/notify_pending_alerts.py --mark-sent
```

## Testy

```powershell
python -m unittest discover -s test -p "test_*.py"
```
