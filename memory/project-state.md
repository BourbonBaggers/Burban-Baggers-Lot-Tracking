# Project State

## Current Phase

M0 - Planning Baseline.

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

No application code exists yet. The first checkpoint is documentation and project history.

## Open Questions

- Local development port is not selected yet.

## Deployment

- Server: `192.168.0.124`
- Deploy user: `jayk1`
- SSH target: `jayk1@192.168.0.124`
- Deploy sequence is not defined yet.
