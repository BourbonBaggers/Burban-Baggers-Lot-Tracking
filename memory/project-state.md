# Project State

## Current Phase

M8 - Hardening and Launch Review complete.

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

M6 printing, label views, and CSV exports have been added and verified:

- Batch detail and checkpoint pages have print-friendly layouts through the existing print
  stylesheet.
- Batch detail page can upload a barcode PNG for the lot.
- Browser print label view is available at `/batches/<lot_number>/label`.
- Uploaded barcode PNGs are stored under the configured upload folder and served through
  `/labels/<id>/barcode`.
- CSV exports are available at `/exports/batches.csv`, `/exports/ingredients.csv`,
  `/exports/qc.csv`, and `/exports/checkpoints.csv`.
- Running app verification uploaded a test PNG for `TC-SYR-20260602-A`, loaded the label
  view, served the PNG, and returned batch/checkpoint CSV data.
- `docker compose run --rm --build app pytest` passes with 12 tests.

M7 product and recipe editor has been added and verified:

- Product list at `/products`.
- Product/recipe editor at `/products/<product_id>`.
- Product fields can update name, code, and active flag.
- Recipe fields can update name, version, active flag, QC targets, hot-fill target,
  expected yield, procedure documentation, and notes.
- Recipe ingredient defaults can be edited in a table and new rows can be added with
  vanilla JavaScript.
- Running app verification saved product fields, recipe fields, and the five seeded
  recipe ingredient defaults for Toasted Cherry Simple Syrup.
- `docker compose run --rm --build app pytest` passes with 14 tests.

M8 launch handoff has been added and verified:

- `docs/launch-handoff.md` documents setup, verification, Docker volumes, backup, restore,
  n8n API authentication, server target, first deploy, later deploys, and remaining
  operational decisions.
- README now reflects the launch handoff status and points to launch docs.
- `CLAUDE.md` and `CLAUDE.local.md` include deploy target notes.
- Final verification commands pass:
  `python3 -m compileall app migrations tests wsgi.py`,
  `docker compose run --rm --build app pytest`,
  and `curl -fsS http://localhost:8020/health`.

Post-M8 product label configuration update:

- UPC barcode image supplied by the user was moved from `app/templates/labels/` to
  `app/static/barcodes/00850078895011-upc-a-sst1.png`.
- Product configuration now includes `shelf_life_months` and `barcode_png_path`.
- Migration `8c2f0b4a91d7_add_product_label_configuration.py` adds those product fields
  and configures Toasted Cherry Simple Syrup with 12 month shelf life and the UPC asset.
- Seed data keeps Toasted Cherry Simple Syrup configured with a 12 month shelf life and
  the UPC barcode.
- The label print view no longer requires per-lot barcode upload. It uses the product
  barcode, displays the lot number, and calculates expiration from product shelf life.
- Running app verification confirmed `/products/1` shows shelf life `12` and barcode path
  `barcodes/00850078895011-upc-a-sst1.png`.
- Running app verification confirmed `/batches/TC-SYR-20260602-A/label` renders the UPC,
  `LOT TC-SYR-20260602-A`, and `EXP 2027-06-02`.
- `docker compose run --rm --build app pytest` passes with 15 tests.

## Open Questions

- Confirm production port and whether the app should remain on `8020`.
- Decide whether production needs HTTPS or local-network-only access.
- Decide backup location and retention schedule.
- Do a real label print test with actual 1.5 inch round label stock.

## Deployment

- Server: `192.168.0.124`
- Deploy user: `jayk1`
- SSH target: `jayk1@192.168.0.124`
- Deploy sequence is documented in `docs/launch-handoff.md`.

## Local Dev

- URL: `http://localhost:8020`
- Health check: `http://localhost:8020/health`
