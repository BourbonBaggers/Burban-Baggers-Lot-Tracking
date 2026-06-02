# Project State

## Current Phase

M1 - Flask Skeleton and Docker complete.

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

## Open Questions

- Core data models are not implemented yet.
- First migration is not implemented yet.

## Deployment

- Server: `192.168.0.124`
- Deploy user: `jayk1`
- SSH target: `jayk1@192.168.0.124`
- Deploy sequence is not defined yet.

## Local Dev

- URL: `http://localhost:8020`
- Health check: `http://localhost:8020/health`
