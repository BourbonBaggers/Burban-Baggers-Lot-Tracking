# Bourbon Baggers Simple Syrup Lot Tracking & QC System
## Product Requirements Document (PRD) for Codex

## Overview

Build an internal-only web application for Bourbon Baggers to manage:

- Simple syrup batch production
- Lot number generation
- Ingredient lot traceability
- Quality control (QC)
- Shelf-life validation
- Retained sample tracking
- Lot label printing

This application is intended for a single user and should prioritize simplicity, traceability, and reliability over flexibility.

---

# Goals

The system must:

1. Generate unique lot numbers.
2. Track ingredient lots used in each batch.
3. Record production data.
4. Record QC measurements.
5. Track retained samples.
6. Schedule shelf-life validation checkpoints.
7. Print lot labels.
8. Expose checkpoint data to n8n.
9. Support future expansion to additional products.
10. Support future migration from SQLite to PostgreSQL.

---

# Non-Goals

Do NOT build:

- User roles
- Multi-user permissions
- Approval workflows
- ERP functionality
- Inventory management beyond batch tracking
- Email notification engine
- Shopify integration
- ShipStation integration

---

# Technology Stack

Required:

- Python
- Flask
- Jinja templates
- SQLAlchemy ORM
- Alembic migrations
- SQLite
- Docker Compose

Architecture requirements:

- Database access through SQLAlchemy
- No SQLite-specific shortcuts
- Clean migration path to PostgreSQL
- Environment-variable configuration
- Uploaded files stored in mounted Docker volume

---

# Product Scope

Initial product supported:

## Toasted Cherry Simple Syrup

Future products may be added later.

The system should support multiple products structurally but only ship with a single seeded product.

---

# Product Definition

A Product owns:

- Product name
- Product code
- Recipe
- QC targets
- Shelf-life schedule
- Procedure documentation

Example:

Name:
Toasted Cherry Simple Syrup

Code:
TC-SYR

---

# Recipe Definition

A recipe belongs to a product.

Recipe fields:

- Recipe name
- Version
- Active flag
- Procedure text
- Notes
- Target pH
- Target Brix
- Target hot-fill temperature
- Expected yield (optional)

Recipe ingredients:

- Ingredient name
- Default quantity
- Default unit
- Sort order
- Notes

---

# Seed Recipe

Water: 5 gallons

Sugar: 37.5 lb

Citric Acid: 57 g

Potassium Sorbate: 37.5 g

Infusion:
Toasted Cherry Bourbon Baggers teabags

Target pH:
3.33

Target Brix:
52

Target Hot Fill Temperature:
195°F

---

# Procedure Storage

The recipe must include a rich text procedure field.

The procedure field is documentation only.

It is NOT a workflow engine.

The initial procedure should support:

1. Steep infusion bags in water.
2. Add sugar.
3. Add citric acid.
4. Add potassium sorbate.
5. Heat product.
6. Bottle hot.
7. Apply induction seal.
8. Apply shrink band.
9. Record production counts.
10. Perform QC.

---

# Lot Numbering

Format:

TC-SYR-YYYYMMDD-A

Examples:

TC-SYR-20260602-A

TC-SYR-20260602-B

Requirements:

- Automatically generated
- Unique
- Searchable
- User editable if necessary

---

# Batch Workflow

1. Create batch.
2. Generate lot number.
3. Load product recipe.
4. Pre-fill ingredient defaults.
5. Enter supplier lots.
6. Enter actual quantities used.
7. Record production events.
8. Record QC.
9. Release or hold batch.
10. Schedule shelf-life checkpoints.

---

# Batch Data

Store:

- Lot number
- Product
- Recipe version
- Production date
- Status
- Notes

Statuses:

- Draft
- In Production
- QC Pending
- Released
- On Hold
- Failed
- Disposed

---

# Ingredient Traceability

Each batch ingredient record stores:

- Ingredient name
- Supplier
- Supplier lot number
- Internal lot number (optional)
- Default quantity
- Actual quantity
- Unit
- Expiration date (optional)
- Notes

---

# Production Tracking

Capture:

- Steep start time
- Steep end time
- Heat start time
- Bottling start time
- Bottling end time
- Bottling start temperature
- Bottling end temperature
- Notes

---

# Bottle Accounting

Track:

- Filled bottles
- Rejected bottles
- Retained samples
- Released bottles
- Disposed bottles

Formula:

Released =
Filled - Rejected - Retained - Disposed

---

# Retained Samples

Retained samples are bottles intentionally kept for future shelf-life testing.

Do not refer to these as "held inventory."

Default recommendation:

Minimum of 4 retained bottles per batch.

One bottle for:

- 3 month checkpoint
- 6 month checkpoint
- 9 month checkpoint
- 12 month checkpoint

---

# Release QC

Store:

- pH
- Brix
- Measurement temperature
- Appearance
- Aroma
- Taste notes
- Seal condition
- Spoilage observed
- Pass/Fail
- Notes

---

# Shelf-Life Validation

When a batch is released, automatically create:

- 3 month checkpoint
- 6 month checkpoint
- 9 month checkpoint
- 12 month checkpoint

Checkpoint status:

- Not Due
- Due Soon
- Due
- Overdue
- Completed
- Failed

Checkpoint captures:

- Inspection date
- pH
- Brix
- Appearance
- Aroma
- Taste notes
- Seal condition
- Spoilage observations
- Pass/Fail
- Notes

---

# Dashboard

Show:

- Recent batches
- QC pending batches
- Released batches
- Failed batches
- Upcoming checkpoints
- Due checkpoints
- Overdue checkpoints
- Retained sample summary

---

# Screens

## Dashboard

Operational summary.

## Batch List

Searchable list of all batches.

## New Batch

Create batch from recipe.

## Batch Detail

Full batch record.

## Product / Recipe

Simple editor for recipe and QC settings.

## Shelf-Life Checkpoints

List of upcoming and overdue validations.

---

# Label Printing

Support lot label printing.

Label size:

1.5 inch round

Label contents:

- Lot number
- Barcode image
- Product code (optional)
- Production date (optional)

Barcode source:

User-supplied PNG.

Implementation:

Browser-based print view.

Future integration with existing label application should be possible.

---

# n8n Integration

The application does not send notifications.

n8n handles notifications.

Provide API endpoints.

## GET /api/checkpoints/due

Returns due and overdue checkpoints.

## GET /api/checkpoints/upcoming?days=30

Returns upcoming checkpoints.

## GET /api/batches/{lot_number}

Returns batch information.

Authentication:

Optional API key via environment variable.

---

# Data Model

## Product

- id
- name
- code
- active
- created_at
- updated_at

## Recipe

- id
- product_id
- version
- active
- target_ph
- target_brix
- target_hot_fill_temp_f
- procedure_text
- notes

## RecipeIngredient

- id
- recipe_id
- ingredient_name
- default_quantity
- default_unit
- sort_order

## Batch

- id
- lot_number
- product_id
- recipe_id
- production_date
- status
- notes

## BatchIngredient

- id
- batch_id
- ingredient_name
- supplier
- supplier_lot
- actual_quantity
- unit

## ProductionRecord

- id
- batch_id
- timestamps
- temperatures
- notes

## BottleCount

- id
- batch_id
- filled_count
- rejected_count
- retained_sample_count
- released_count
- disposed_count

## QCRecord

- id
- batch_id
- qc_type
- ph
- brix
- results
- notes

## ShelfLifeCheckpoint

- id
- batch_id
- checkpoint_month
- due_date
- status

## LotLabel

- id
- batch_id
- barcode_png_path

---

# Acceptance Criteria

The system is complete when:

1. User can create a syrup batch.
2. Lot number is generated automatically.
3. Recipe loads automatically.
4. Ingredient lots are recorded.
5. Actual quantities can be overridden.
6. Production data is recorded.
7. QC data is recorded.
8. Retained samples are tracked.
9. Shelf-life checkpoints are generated automatically.
10. Dashboard displays due and overdue checkpoints.
11. n8n can retrieve checkpoint information through API.
12. Lot labels print correctly.
13. Batch records are printable.
14. CSV exports are available.
15. Application runs in Docker.
16. SQLite can later be migrated to PostgreSQL.
