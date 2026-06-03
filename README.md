# Burban Baggers Lot Tracking

Internal lot tracking and QC system for Bourbon Baggers simple syrup production.

The initial application will support Toasted Cherry Simple Syrup batch creation, lot
number generation, ingredient traceability, production records, release QC, retained
samples, shelf-life validation checkpoints, printable labels, printable batch records,
CSV exports, and n8n API access.

## Current Status

Launch handoff checkpoint. The app has batch creation, lot traceability, production
records, release QC, retained samples, shelf-life checkpoints, CSV exports, label printing,
and product/recipe editing.

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

Lot labels use the barcode PNG and shelf-life months configured on the product. The
Toasted Cherry Simple Syrup seed uses a 12 month shelf life and this UPC asset:

```text
app/static/barcodes/00850078895011-upc-a-sst1.png
```

Print the browser label view:

```text
/batches/{lot_number}/label
```

## Products And Recipes

```text
/products
/products/{product_id}
```

See:

- `docs/Bourbon_Baggers_Simple_Syrup_PRD_For_Codex.md`
- `docs/history-plan.md`
- `docs/launch-handoff.md`
- `memory/project-state.md`
