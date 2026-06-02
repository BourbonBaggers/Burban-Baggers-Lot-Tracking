# Launch Handoff

## Current App

Internal Flask/Jinja app for Bourbon Baggers simple syrup lot tracking, QC, retained
samples, shelf-life checkpoints, label printing, CSV exports, and n8n API access.

Local URL:

```text
http://localhost:8020
```

Health check:

```text
http://localhost:8020/health
```

## Setup

```bash
cp .env.example .env
docker compose up --build -d
docker compose run --rm app alembic upgrade head
docker compose run --rm app flask seed-data
```

## Verification

```bash
python3 -m compileall app migrations tests wsgi.py
docker compose run --rm --build app pytest
curl -fsS http://localhost:8020/health
```

Expected test count at this checkpoint:

```text
14 passed
```

## Data

Docker volumes:

```text
lottracking_lot_tracking_data
lottracking_lot_tracking_uploads
```

SQLite path inside the app container:

```text
/data/lot_tracking.sqlite3
```

Upload path inside the app container:

```text
/uploads
```

## Backup

Stop the app or make sure no writes are happening, then copy the database and uploads:

```bash
docker compose stop app
docker run --rm -v lottracking_lot_tracking_data:/data -v "$PWD/backups":/backup alpine cp /data/lot_tracking.sqlite3 /backup/lot_tracking.sqlite3
docker run --rm -v lottracking_lot_tracking_uploads:/uploads -v "$PWD/backups":/backup alpine sh -c 'cd /uploads && tar czf /backup/uploads.tar.gz .'
docker compose up -d
```

## Restore

```bash
docker compose stop app
docker run --rm -v lottracking_lot_tracking_data:/data -v "$PWD/backups":/backup alpine cp /backup/lot_tracking.sqlite3 /data/lot_tracking.sqlite3
docker run --rm -v lottracking_lot_tracking_uploads:/uploads -v "$PWD/backups":/backup alpine sh -c 'cd /uploads && tar xzf /backup/uploads.tar.gz'
docker compose up -d
```

## n8n API

Set `API_KEY` in the app environment to require authentication. n8n can pass the key as
`X-API-Key` or as `Authorization: Bearer <key>`.

Endpoints:

```text
GET /api/checkpoints/due
GET /api/checkpoints/upcoming?days=30
GET /api/batches/{lot_number}
```

## Deployment Target

Server:

```text
jayk1@192.168.0.124
```

Suggested first deploy shape:

```bash
ssh jayk1@192.168.0.124
git clone https://github.com/BourbonBaggers/Burban-Baggers-Lot-Tracking.git
cd Burban-Baggers-Lot-Tracking
cp .env.example .env
docker compose up --build -d
docker compose run --rm app alembic upgrade head
docker compose run --rm app flask seed-data
```

For later deploys:

```bash
ssh jayk1@192.168.0.124
cd Burban-Baggers-Lot-Tracking
git pull
docker compose up --build -d
docker compose run --rm app alembic upgrade head
```

## Remaining Work

- Confirm production port and whether this should stay on `8020`.
- Decide whether the server needs HTTPS or local-network-only access.
- Decide backup location and retention schedule.
- Do a real label print test with the actual 1.5 inch round label stock.
