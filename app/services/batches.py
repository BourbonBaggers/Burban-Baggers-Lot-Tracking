from datetime import date

from app.models import Batch


LOT_SUFFIXES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def calculate_released_count(
    filled_count,
    rejected_count,
    retained_sample_count,
    disposed_count,
):
    return filled_count - rejected_count - retained_sample_count - disposed_count


def next_lot_number(product_code, production_date, existing_lot_numbers):
    prefix = lot_prefix(product_code, production_date)
    used_suffixes = {
        lot_number.rsplit("-", 1)[-1]
        for lot_number in existing_lot_numbers
        if lot_number.startswith(f"{prefix}-")
    }

    for suffix in LOT_SUFFIXES:
        if suffix not in used_suffixes:
            return f"{prefix}-{suffix}"

    raise ValueError(f"No lot suffixes remain for {prefix}")


def generate_lot_number(product_code, production_date=None):
    production_date = production_date or date.today()
    prefix = lot_prefix(product_code, production_date)
    existing_lots = (
        Batch.query.filter(Batch.lot_number.like(f"{prefix}-%"))
        .with_entities(Batch.lot_number)
        .all()
    )
    return next_lot_number(product_code, production_date, [lot[0] for lot in existing_lots])


def lot_prefix(product_code, production_date):
    return f"{product_code}-{production_date:%Y%m%d}"
