# Burban Baggers Lot Tracking

Internal lot tracking and QC system for Bourbon Baggers simple syrup production.

The initial application will support Toasted Cherry Simple Syrup batch creation, lot
number generation, ingredient traceability, production records, release QC, retained
samples, shelf-life validation checkpoints, printable labels, printable batch records,
CSV exports, and n8n API access.

## Current Status

M1 skeleton in progress. The app has a Flask/Jinja shell, environment configuration,
SQLAlchemy/Alembic wiring, and Docker Compose.

## Run Locally

```bash
docker compose up --build
```

Open:

```text
http://localhost:8020
```

Health check:

```text
http://localhost:8020/health
```

## Database

```bash
docker compose run --rm app alembic upgrade head
docker compose run --rm app flask seed-data
```

## Tests

```bash
docker compose run --rm app pytest
```

## n8n API

If `API_KEY` is set, pass it as `X-API-Key` or as a bearer token.

```text
GET /api/checkpoints/due
GET /api/checkpoints/upcoming?days=30
GET /api/batches/{lot_number}
```

## CSV Exports

```text
GET /exports/batches.csv
GET /exports/ingredients.csv
GET /exports/qc.csv
GET /exports/checkpoints.csv
```

## Lot Labels

Upload a barcode PNG from the batch detail page, then print the browser label view:

```text
/batches/{lot_number}/label
```

See:

- `docs/Bourbon_Baggers_Simple_Syrup_PRD_For_Codex.md`
- `docs/history-plan.md`
- `memory/project-state.md`
