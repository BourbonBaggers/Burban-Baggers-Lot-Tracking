# Project History Plan

This project should remain resumable from Git history at every major checkpoint.
Each milestone ends with a commit that leaves the repository in a coherent state.

## Checkpoint Rules

- Commit at each milestone before moving to the next major body of work.
- Keep commit messages direct and searchable.
- Before every push, update `memory/project-state.md`, `memory/feedback-session.md`,
  and `memory/MEMORY.md` when there is new durable context.
- Do not skip tests just to create a checkpoint. If tests cannot run, document why in
  the final session note and memory when the reason is durable.
- Keep the app simple: server-rendered Flask/Jinja first, minimal JavaScript only where
  it improves data entry, validation, or printing.

## Milestones

### M0 - Planning Baseline

Goal: Capture requirements, UX constraints, project memory, and Git/GitHub baseline.

Deliverables:

- Requirements and Claude context reviewed.
- `README.md`, `CLAUDE.md`, `docs/history-plan.md`, and `memory/` context created.
- Local Git repository initialized.
- Public GitHub repository created as `Burban Baggers Lot Tracking`.

Commit:

- `docs: establish project baseline`

### M1 - Flask Skeleton and Docker

Goal: Create a runnable Flask app with database configuration and development workflow.

Deliverables:

- Flask application factory.
- Dockerfile and Docker Compose.
- Environment-variable configuration.
- SQLite volume path configured for Docker.
- Alembic initialized.
- Basic health page and app layout.

Commit:

- `build: add flask docker skeleton`

### M2 - Core Data Model and Seed Data

Goal: Implement schema foundations without UI complexity.

Deliverables:

- SQLAlchemy models for products, recipes, recipe ingredients, batches, ingredients,
  production records, bottle counts, QC records, shelf-life checkpoints, and labels.
- Alembic migration.
- Seed data for Toasted Cherry Simple Syrup and recipe defaults.
- Basic tests for lot numbering and bottle count formula.

Commit:

- `feat: add core lot tracking schema`

### M3 - Batch Creation and Fast Data Entry

Goal: Make the primary production workflow usable.

Deliverables:

- Batch list, new batch form, and batch detail screen.
- Automatic lot number generation with editable override.
- Recipe defaults copied into batch ingredients.
- Fast-edit forms for ingredient lots and actual quantities.
- Thin JSON mutation endpoints backed by service functions.

Commit:

- `feat: create batch workflow`

### M4 - Production Records, Bottle Counts, and Release QC

Goal: Capture the operational data needed to release or hold a batch.

Deliverables:

- Production timing and temperature form.
- Bottle accounting with released count calculated from filled, rejected, retained,
  and disposed counts.
- Release QC form and pass/fail handling.
- Status transitions for Draft, In Production, QC Pending, Released, On Hold, Failed,
  and Disposed.

Commit:

- `feat: add production and release qc`

### M5 - Shelf-Life Checkpoints and n8n API

Goal: Support retained sample validation and external notification workflows.

Deliverables:

- Automatic 3, 6, 9, and 12 month checkpoint creation on release.
- Checkpoint list with due, upcoming, overdue, completed, and failed states.
- Checkpoint completion form.
- `GET /api/checkpoints/due`.
- `GET /api/checkpoints/upcoming?days=30`.
- `GET /api/batches/{lot_number}`.
- Optional API key protection from environment.

Commit:

- `feat: add shelf life checkpoints api`

### M6 - Printing and CSV Exports

Goal: Make records portable for production, QC, and audit use.

Deliverables:

- Print stylesheet for dashboard, batch list, batch detail, product/recipe, and
  checkpoint screens.
- Browser print view for 1.5 inch round lot labels using uploaded barcode PNGs.
- CSV exports for batches, ingredients, QC records, and checkpoints.

Commit:

- `feat: add printing and exports`

### M7 - Product and Recipe Editor

Goal: Allow future products while keeping the initial scope focused.

Deliverables:

- Product and recipe editor.
- Recipe ingredient editor.
- Active recipe selection.
- Procedure documentation editor.
- No workflow engine.

Commit:

- `feat: add product recipe editor`

### M8 - Hardening and Launch Review

Goal: Leave the internal tool reliable, understandable, and easy to recover.

Deliverables:

- Form validation pass.
- Print layout pass.
- Desktop and tablet layout pass.
- Migration path reviewed for PostgreSQL portability.
- README updated with setup, run, test, and backup notes.
- Memory updated with final launch state.

Commit:

- `docs: prepare launch handoff`

