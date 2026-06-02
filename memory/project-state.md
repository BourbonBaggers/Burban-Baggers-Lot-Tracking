# Project State

## Current Phase

M5 - Shelf-Life Checkpoints and n8n API complete.

## Product

Burban Baggers Lot Tracking is an internal-only Flask application for Bourbon Baggers
simple syrup batch tracking, lot traceability, QC, retained samples, shelf-life
checkpoints, label printing, CSV exports, and n8n API access.

Initial product: Toasted Cherry Simple Syrup.

## Durable Decisions

- Stack: Python, Flask, Jinja templates, SQLAlchemy ORM, Alembic, SQLite, Docker Compose.
- Architecture: API-first for mutations. Templates are display-only. Business logic belongs
  in services. Route handlers stay thin.
- Storage: avoid SQLite-specific shortcuts so PostgreSQL migration remains feasible.
- UX: internal tool, desktop-first, tablet-friendly, fast data entry, forms and tables over
  decorative dashboards, print-friendly major screens, minimal JavaScript.
- Scope: single-user internal tool with no roles, permissions, approval workflows, ERP,
  broad inventory management, email notification engine, Shopify, or ShipStation.

## Repository Status

M0 is committed and pushed to GitHub.

M1 app skeleton has been added and verified:

- Flask application factory.
- Jinja base layout and placeholder production dashboard.
- Print-friendly base stylesheet.
- Environment-variable configuration.
- SQLAlchemy extension.
- Alembic environment.
- Dockerfile and Docker Compose using port `8020`.
- `python3 -m compileall app migrations wsgi.py` passes.
- `docker compose up --build` runs successfully.
- `GET /health` returns `{"status":"ok"}`.
- `docker compose exec app alembic current` loads the migration environment.

M2 core data layer has been added and verified:

- SQLAlchemy models for products, recipes, recipe ingredients, batches, batch ingredients,
  production records, bottle counts, QC records, shelf-life checkpoints, and lot labels.
- Alembic migration `de605f321afb_add_core_lot_tracking_schema.py`.
- Seed command `flask seed-data` for Toasted Cherry Simple Syrup.
- Batch service functions for lot-number suffixing and released bottle counts.
- Pytest coverage for lot-number suffix selection, suffix exhaustion, and released count.
- `docker compose run --rm --build app alembic upgrade head` passes.
- `docker compose run --rm app flask seed-data` passes.
- `docker compose run --rm --build app pytest` passes with 3 tests.
- Detached app responds at `http://localhost:8020/health`.

M3 batch workflow has been added and verified:

- Batch list at `/batches`.
- New batch form at `/batches/new`.
- Batch detail page at `/batches/<lot_number>`.
- Navigation links for batch list and new batch.
- `POST /api/batches` creates a draft batch, auto-generates the next lot number, and
  copies recipe ingredients to the batch.
- `PATCH /api/batches/<id>/ingredients` saves supplier lots, internal lots, actual
  quantities, units, expiration dates, and notes.
- Minimal vanilla JavaScript submits JSON mutations and redirects after batch creation.
- Batch detail screen has a print button and print-friendly styling.
- `docker compose run --rm --build app pytest` passes with 4 tests.
- Verification batch `TC-SYR-20260602-A` was created in the local Docker SQLite volume.
- Ingredient save was verified through the running app.

M4 production and release workflow has been added and verified:

- Batch detail page now includes compact forms for status, production record, bottle counts,
  and release QC.
- `PATCH /api/batches/<id>/status` updates Draft, In Production, QC Pending, Released,
  On Hold, Failed, and Disposed statuses.
- `PATCH /api/batches/<id>/production` saves steep, heat, bottling, temperature, and notes.
- `PATCH /api/batches/<id>/bottle-count` saves bottle accounting and calculates released
  count as filled - rejected - retained - disposed.
- `PATCH /api/batches/<id>/release-qc` saves pH, Brix, measurement temperature, sensory
  notes, seal condition, spoilage observed, pass/fail, and notes.
- `docker compose run --rm --build app pytest` passes with 6 tests.
- Running app verification updated `TC-SYR-20260602-A` to Released with production data,
  release QC, and released count `110`.

M5 shelf-life checkpoints and n8n API have been added and verified:

- Releasing a batch creates missing 3, 6, 9, and 12 month shelf-life checkpoints.
- Checkpoint list at `/checkpoints` supports row selection and completion entry.
- `PATCH /api/checkpoints/<id>` saves inspection date, pH, Brix, pass/fail, sensory
  observations, spoilage observations, and notes.
- `GET /api/checkpoints/due` returns due and overdue incomplete checkpoints.
- `GET /api/checkpoints/upcoming?days=30` returns upcoming incomplete checkpoints.
- `GET /api/batches/<lot_number>` returns batch, ingredient, and checkpoint JSON.
- n8n API endpoints use optional `API_KEY` from the environment, accepted as `X-API-Key`
  or bearer token.
- Gunicorn now runs with 2 workers and 4 threads. Batch creation timing improved from
  about 17 seconds in the observed local hang case to about 0.04 seconds by preventing one
  idle sync worker connection from blocking the app.
- `docker compose run --rm --build app pytest` passes with 11 tests.
- Running app verification created four checkpoints for `TC-SYR-20260602-A`, returned the
  3 month checkpoint from the upcoming API, completed checkpoint `1`, and confirmed the
  due API returned no incomplete due checkpoints.

## Open Questions

- Printing, label views, and CSV exports are not implemented yet.

## Deployment

- Server: `192.168.0.124`
- Deploy user: `jayk1`
- SSH target: `jayk1@192.168.0.124`
- Deploy sequence is not defined yet.

## Local Dev

- URL: `http://localhost:8020`
- Health check: `http://localhost:8020/health`
