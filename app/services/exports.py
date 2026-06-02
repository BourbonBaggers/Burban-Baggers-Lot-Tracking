import csv
from io import StringIO

from flask import Response

from app.models import Batch, BatchIngredient, QCRecord, ShelfLifeCheckpoint


def csv_response(filename, headers, rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def batches_csv():
    batches = Batch.query.order_by(Batch.production_date.desc(), Batch.id.desc()).all()
    return csv_response(
        "batches.csv",
        ["lot_number", "product", "production_date", "status", "notes"],
        [
            [
                batch.lot_number,
                batch.product.name,
                batch.production_date.isoformat(),
                batch.status,
                batch.notes,
            ]
            for batch in batches
        ],
    )


def ingredients_csv():
    ingredients = BatchIngredient.query.join(Batch).order_by(Batch.lot_number).all()
    return csv_response(
        "batch_ingredients.csv",
        [
            "lot_number",
            "ingredient",
            "supplier",
            "supplier_lot",
            "internal_lot",
            "actual_quantity",
            "unit",
            "expiration_date",
            "notes",
        ],
        [
            [
                item.batch.lot_number,
                item.ingredient_name,
                item.supplier,
                item.supplier_lot,
                item.internal_lot,
                item.actual_quantity,
                item.unit,
                item.expiration_date.isoformat() if item.expiration_date else "",
                item.notes,
            ]
            for item in ingredients
        ],
    )


def qc_csv():
    records = QCRecord.query.join(Batch).order_by(Batch.lot_number, QCRecord.id).all()
    return csv_response(
        "qc_records.csv",
        [
            "lot_number",
            "qc_type",
            "ph",
            "brix",
            "measurement_temp_f",
            "spoilage_observed",
            "passed",
            "notes",
        ],
        [
            [
                record.batch.lot_number,
                record.qc_type,
                record.ph or "",
                record.brix or "",
                record.measurement_temp_f or "",
                record.spoilage_observed,
                record.passed,
                record.notes,
            ]
            for record in records
        ],
    )


def checkpoints_csv():
    checkpoints = (
        ShelfLifeCheckpoint.query.join(Batch)
        .order_by(ShelfLifeCheckpoint.due_date, ShelfLifeCheckpoint.id)
        .all()
    )
    return csv_response(
        "shelf_life_checkpoints.csv",
        [
            "lot_number",
            "checkpoint_month",
            "due_date",
            "status",
            "inspection_date",
            "ph",
            "brix",
            "passed",
            "notes",
        ],
        [
            [
                checkpoint.batch.lot_number,
                checkpoint.checkpoint_month,
                checkpoint.due_date.isoformat(),
                checkpoint.status,
                checkpoint.inspection_date.isoformat()
                if checkpoint.inspection_date
                else "",
                checkpoint.ph or "",
                checkpoint.brix or "",
                checkpoint.passed,
                checkpoint.notes,
            ]
            for checkpoint in checkpoints
        ],
    )
