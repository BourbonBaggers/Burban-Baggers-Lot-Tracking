from datetime import date, timedelta

from app.extensions import db
from app.models import Batch, ShelfLifeCheckpoint


CHECKPOINT_MONTHS = (3, 6, 9, 12)


def create_release_checkpoints(batch):
    existing_months = {
        checkpoint.checkpoint_month for checkpoint in batch.shelf_life_checkpoints
    }

    for month in CHECKPOINT_MONTHS:
        if month in existing_months:
            continue

        db.session.add(
            ShelfLifeCheckpoint(
                batch=batch,
                checkpoint_month=month,
                due_date=add_months(batch.production_date, month),
                status="Not Due",
            )
        )


def update_checkpoint(checkpoint_id, data):
    checkpoint = db.session.get(ShelfLifeCheckpoint, checkpoint_id)
    if checkpoint is None:
        raise ValueError("Checkpoint not found")

    checkpoint.inspection_date = parse_date(data.get("inspection_date"))
    checkpoint.ph = data.get("ph") or None
    checkpoint.brix = data.get("brix") or None
    checkpoint.appearance = data.get("appearance", "").strip()
    checkpoint.aroma = data.get("aroma", "").strip()
    checkpoint.taste_notes = data.get("taste_notes", "").strip()
    checkpoint.seal_condition = data.get("seal_condition", "").strip()
    checkpoint.spoilage_observations = data.get("spoilage_observations", "").strip()
    checkpoint.passed = parse_optional_bool(data.get("passed"))
    checkpoint.notes = data.get("notes", "").strip()

    if checkpoint.passed is False:
        checkpoint.status = "Failed"
    elif checkpoint.inspection_date:
        checkpoint.status = "Completed"
    else:
        checkpoint.status = checkpoint_status(checkpoint.due_date)

    db.session.commit()
    return checkpoint


def due_checkpoints(today=None):
    today = today or date.today()
    return (
        ShelfLifeCheckpoint.query.filter(
            ShelfLifeCheckpoint.due_date <= today,
            ShelfLifeCheckpoint.status.notin_(["Completed", "Failed"]),
        )
        .order_by(ShelfLifeCheckpoint.due_date, ShelfLifeCheckpoint.id)
        .all()
    )


def upcoming_checkpoints(days=30, today=None):
    today = today or date.today()
    end_date = today + timedelta(days=days)
    return (
        ShelfLifeCheckpoint.query.filter(
            ShelfLifeCheckpoint.due_date > today,
            ShelfLifeCheckpoint.due_date <= end_date,
            ShelfLifeCheckpoint.status.notin_(["Completed", "Failed"]),
        )
        .order_by(ShelfLifeCheckpoint.due_date, ShelfLifeCheckpoint.id)
        .all()
    )


def refresh_checkpoint_statuses(checkpoints, today=None):
    today = today or date.today()
    for checkpoint in checkpoints:
        if checkpoint.status in {"Completed", "Failed"}:
            continue
        checkpoint.status = checkpoint_status(checkpoint.due_date, today)
    db.session.commit()
    return checkpoints


def checkpoint_status(due_date, today=None):
    today = today or date.today()
    if due_date < today:
        return "Overdue"
    if due_date == today:
        return "Due"
    if due_date <= today + timedelta(days=14):
        return "Due Soon"
    return "Not Due"


def checkpoint_to_dict(checkpoint):
    batch = checkpoint.batch
    return {
        "id": checkpoint.id,
        "lot_number": batch.lot_number,
        "product": batch.product.name,
        "product_code": batch.product.code,
        "checkpoint_month": checkpoint.checkpoint_month,
        "due_date": checkpoint.due_date.isoformat(),
        "status": checkpoint.status,
        "inspection_date": checkpoint.inspection_date.isoformat()
        if checkpoint.inspection_date
        else None,
        "passed": checkpoint.passed,
        "ph": float(checkpoint.ph) if checkpoint.ph is not None else None,
        "brix": float(checkpoint.brix) if checkpoint.brix is not None else None,
        "notes": checkpoint.notes,
    }


def batch_to_dict(batch):
    return {
        "id": batch.id,
        "lot_number": batch.lot_number,
        "product": batch.product.name,
        "product_code": batch.product.code,
        "recipe_version": batch.recipe.version,
        "production_date": batch.production_date.isoformat(),
        "status": batch.status,
        "notes": batch.notes,
        "ingredients": [
            {
                "ingredient_name": ingredient.ingredient_name,
                "supplier": ingredient.supplier,
                "supplier_lot": ingredient.supplier_lot,
                "internal_lot": ingredient.internal_lot,
                "actual_quantity": float(ingredient.actual_quantity),
                "unit": ingredient.unit,
                "expiration_date": ingredient.expiration_date.isoformat()
                if ingredient.expiration_date
                else None,
                "notes": ingredient.notes,
            }
            for ingredient in batch.ingredients
        ],
        "checkpoints": [
            checkpoint_to_dict(checkpoint)
            for checkpoint in batch.shelf_life_checkpoints
        ],
    }


def add_months(start_date, months):
    year = start_date.year + (start_date.month - 1 + months) // 12
    month = (start_date.month - 1 + months) % 12 + 1
    day = min(start_date.day, days_in_month(year, month))
    return date(year, month, day)


def days_in_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day


def parse_date(value):
    return date.fromisoformat(value) if value else None


def parse_optional_bool(value):
    if value == "":
        return None
    return str(value).lower() in {"true", "1", "yes", "on"}
