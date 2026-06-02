from datetime import date

import pytest

from app.services.batches import calculate_released_count, next_lot_number


def test_next_lot_number_uses_first_available_suffix():
    lot_number = next_lot_number(
        "TC-SYR",
        date(2026, 6, 2),
        [
            "TC-SYR-20260602-A",
            "TC-SYR-20260602-B",
            "TC-SYR-20260601-A",
        ],
    )

    assert lot_number == "TC-SYR-20260602-C"


def test_next_lot_number_raises_when_day_is_full():
    existing = [f"TC-SYR-20260602-{suffix}" for suffix in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    with pytest.raises(ValueError):
        next_lot_number("TC-SYR", date(2026, 6, 2), existing)


def test_calculate_released_count():
    released_count = calculate_released_count(
        filled_count=120,
        rejected_count=5,
        retained_sample_count=4,
        disposed_count=1,
    )

    assert released_count == 110
