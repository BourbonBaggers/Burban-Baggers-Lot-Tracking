from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models import Batch, BottleCount, ProductionRecord, QCRecord
from app.services.batches import calculate_released_count
from app.services.checkpoints import create_release_checkpoints


BATCH_STATUSES = {
    "Draft",
    "In Production",
    "QC Pending",
    "Released",
    "On Hold",
    "Failed",
    "Disposed",
}


def update_batch_status(batch_id, status):
    if status not in BATCH_STATUSES:
        raise ValueError("Invalid batch status")

    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")

    batch.status = status
    if status == "Released":
        create_release_checkpoints(batch)

    db.session.commit()
    return batch


def update_production_record(batch_id, data):
    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")

    record = batch.production_record or ProductionRecord(batch=batch)
    db.session.add(record)

    record.steep_start_time = parse_datetime(data.get("steep_start_time"))
    record.steep_end_time = parse_datetime(data.get("steep_end_time"))
    record.heat_start_time = parse_datetime(data.get("heat_start_time"))
    record.bottling_start_time = parse_datetime(data.get("bottling_start_time"))
    record.bottling_end_time = parse_datetime(data.get("bottling_end_time"))
    record.bottling_start_temp_f = parse_decimal(data.get("bottling_start_temp_f"))
    record.bottling_end_temp_f = parse_decimal(data.get("bottling_end_temp_f"))
    record.notes = data.get("notes", "").strip()

    db.session.commit()
    return record


def update_bottle_count(batch_id, data):
    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")

    count = batch.bottle_count or BottleCount(batch=batch)
    db.session.add(count)

    count.filled_count = parse_int(data.get("filled_count"))
    count.rejected_count = parse_int(data.get("rejected_count"))
    count.retained_sample_count = parse_int(data.get("retained_sample_count"))
    count.disposed_count = parse_int(data.get("disposed_count"))
    count.released_count = calculate_released_count(
        count.filled_count,
        count.rejected_count,
        count.retained_sample_count,
        count.disposed_count,
    )

    db.session.commit()
    return count


def update_release_qc(batch_id, data):
    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")

    record = next((qc for qc in batch.qc_records if qc.qc_type == "Release"), None)
    if record is None:
        record = QCRecord(batch=batch, qc_type="Release")
        db.session.add(record)

    record.ph = parse_decimal(data.get("ph"))
    record.brix = parse_decimal(data.get("brix"))
    record.measurement_temp_f = parse_decimal(data.get("measurement_temp_f"))
    record.appearance = data.get("appearance", "").strip()
    record.aroma = data.get("aroma", "").strip()
    record.taste_notes = data.get("taste_notes", "").strip()
    record.seal_condition = data.get("seal_condition", "").strip()
    record.spoilage_observed = parse_bool(data.get("spoilage_observed"))
    record.passed = parse_optional_bool(data.get("passed"))
    record.notes = data.get("notes", "").strip()

    db.session.commit()
    return record


def parse_datetime(value):
    return datetime.fromisoformat(value) if value else None


def parse_decimal(value):
    return Decimal(value) if value else None


def parse_int(value):
    return int(value) if value else 0


def parse_bool(value):
    return str(value).lower() in {"true", "1", "yes", "on"}


def parse_optional_bool(value):
    if value == "":
        return None
    return parse_bool(value)
