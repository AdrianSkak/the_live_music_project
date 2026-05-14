# The Live Music Project

The Live Music Project is a small MVP for tracking upcoming concerts by artists
you care about.

The goal is simple: help users find out when followed bands announce concerts
near selected locations, before tickets are sold out or the event has already
passed.

## What It Does

The current version focuses on the core data pipeline:

- stores followed artists, locations, events, and alerts,
- collects concert data from selected web sources,
- parses artist tour pages,
- saves normalized events,
- matches events against tracked locations,
- lists pending concert alerts.

This is not a full product yet. There is no user interface, account system, or
production notification channel. The project is intentionally kept small while
the MVP pipeline is being validated.

## Current Scope

The current implementation supports a small set of real artist sources and a
local PostgreSQL database.

The next natural steps are:

- add more reliable artist sources,
- improve event deduplication,
- improve location matching,
- improve email and WhatsApp notifications,
- add a lightweight API or UI later.

## Tech Stack

- Python
- PostgreSQL
- Docker Compose

## Getting Started

Start the local database:

```powershell
docker compose up -d
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set the database URL if needed:

```powershell
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/live_music"
```

Database schema and seed files are kept in `sql/schema` and `sql/seed`.

## Useful Commands

Check the current pipeline status:

```powershell
python scripts/check_pipeline_status.py
```

Run the scrapers:

```powershell
python scripts/run_scrapers.py
```

Print pending alerts:

```powershell
python scripts/notify_pending_alerts.py
```

Preview a pending alert email:

```powershell
python scripts/send_pending_alert_emails.py
```

Send pending alerts by email:

```powershell
python scripts/send_pending_alert_emails.py --send
```

Run tests:

```powershell
python -m unittest discover -s test -p "test_*.py"
```

## Project Status

Early MVP. The repository is mainly focused on proving that the concert
collection and alert pipeline can work end to end before adding larger product
features.
