# Lot Tracking

## Project Overview
Internal-only lot tracking and QC system for Bourbon Baggers simple syrup production.

The app manages batch creation, automatic lot numbers, ingredient lot traceability,
production records, QC, retained samples, shelf-life checkpoints, printable batch records,
printable 1.5 inch lot labels, CSV exports, and read-only n8n API endpoints.

Primary product for initial launch: Toasted Cherry Simple Syrup.

## Stack
- Python
- Flask
- Jinja templates
- SQLAlchemy ORM
- Alembic migrations
- SQLite for initial storage
- Docker Compose
- Minimal JavaScript only where it clearly improves data entry or printing

## Key Directories

```
app/        Flask application, templates, static assets, and route modules
docs/       Product requirements, history plan, and implementation notes
memory/     Durable project/session context to update before every push
migrations/ Alembic migration environment and versions
.claude/    Claude workflow settings, commands, agents, and hooks
```

## Dev Workflow

```bash
docker compose up --build
docker compose down
docker compose logs -f
docker compose run --rm app alembic upgrade head
docker compose run --rm app flask seed-data
docker compose run --rm app pytest
```

## Deploy

```bash
# Deployment target not selected yet.
```

## Security
- Single-user internal tool.
- No roles or multi-user permissions in initial scope.
- API key for n8n endpoints is optional and environment-variable based.
- `.env` is gitignored and must never be committed.
- Uploaded files, including barcode PNGs, are stored in a mounted Docker volume.

## Local Dev

- Default local URL: `http://localhost:8020`
- Health check: `http://localhost:8020/health`
- Gunicorn runs with 2 workers and 4 threads to avoid one slow local connection blocking
  internal data-entry actions.

## UX Constraints
- Internal production/QC tool, not customer-facing.
- Optimize for speed of data entry.
- Desktop-first, tablet-friendly.
- Favor forms, lists, and tables over dashboard flourishes.
- Minimize clicks and avoid unnecessary navigation.
- Every major screen should have a print-friendly layout.
- Avoid unnecessary JavaScript frameworks unless the implementation clearly benefits.

## Rules

### Code Style
- No comments unless the WHY is non-obvious
- No multi-line docstrings or comment blocks
- No error handling for scenarios that can't happen — trust internal guarantees
- No abstractions, refactors, or features beyond what the task requires
- **Templates and markup live in files, never in Python.** HTML goes in `.html` template files.
  Never assign multi-line HTML/CSS to a Python variable as an escaped string.
- **API-first architecture.** Every mutation goes through a REST endpoint (JSON).
  Templates are display-only. Business logic lives in services, not route handlers or templates.
  Route handlers are thin: validate → call service → return.
- **Shared logic belongs in helpers, not repeated inline.** Check if a utility function already
  exists before writing general-purpose logic. Common operations go in a shared module.

### Git
- Never commit unless explicitly asked
- Never force-push, reset --hard, or run destructive git ops without confirmation
- Never skip hooks (--no-verify)
- .env is gitignored — never commit secrets

### Memory — Update on Every Push
Before every `git push`, update memory so the next session starts with full context.

What to update:
- `memory/project-state.md` — current build phase, prod status, any new bugs fixed or design
  decisions made, anything that changed about the running system
- `memory/feedback-session.md` — any new behavioral feedback or corrections from this session
- `memory/MEMORY.md` index — add pointers to any new memory files

What counts as a memory-worthy change:
- A phase completed or a major feature shipped
- A bug fixed that revealed a non-obvious pattern (document the pattern, not just the fix)
- A design decision made that isn't obvious from reading the code
- Any correction given about how to work on this project

Do not save: ephemeral task state, what files were edited, things already captured in git history.
Memory is for what future-Claude can't derive from reading the repo.

### Responses
- No emojis unless explicitly requested
- Concise — one sentence of context, then the work
- No trailing summaries of what was just done

### What Not To Build
<!-- List explicit out-of-scope items here. -->
