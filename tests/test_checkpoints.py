from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient
from app.services.batches import create_batch
from app.services.checkpoints import (
    add_months,
    batch_to_dict,
    checkpoint_status,
    checkpoint_to_dict,
    due_checkpoints,
    upcoming_checkpoints,
)
from app.services.production import update_batch_status


class TestConfig:
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/tmp/lot-tracking-test-uploads"
    API_KEY = ""


@pytest.fixture
def app_context():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def test_release_creates_four_shelf_life_checkpoints(app_context):
    batch = create_test_batch(date(2026, 6, 2))

    update_batch_status(batch.id, "Released")

    assert [item.checkpoint_month for item in batch.shelf_life_checkpoints] == [3, 6, 9, 12]
    assert [item.due_date for item in batch.shelf_life_checkpoints] == [
        date(2026, 9, 2),
        date(2026, 12, 2),
        date(2027, 3, 2),
        date(2027, 6, 2),
    ]


def test_due_and_upcoming_checkpoint_queries(app_context):
    batch = create_test_batch(date(2026, 1, 1))
    update_batch_status(batch.id, "Released")

    due = due_checkpoints(today=date(2026, 4, 1))
    upcoming = upcoming_checkpoints(days=100, today=date(2026, 4, 1))

    assert [item.checkpoint_month for item in due] == [3]
    assert [item.checkpoint_month for item in upcoming] == [6]


def test_checkpoint_and_batch_serializers(app_context):
    batch = create_test_batch(date(2026, 6, 2))
    update_batch_status(batch.id, "Released")

    checkpoint_payload = checkpoint_to_dict(batch.shelf_life_checkpoints[0])
    batch_payload = batch_to_dict(batch)

    assert checkpoint_payload["lot_number"] == "TC-SYR-20260602-A"
    assert checkpoint_payload["checkpoint_month"] == 3
    assert batch_payload["ingredients"][0]["ingredient_name"] == "Sugar"
    assert len(batch_payload["checkpoints"]) == 4


def test_add_months_handles_short_months():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_checkpoint_status():
    assert checkpoint_status(date(2026, 6, 1), today=date(2026, 6, 2)) == "Overdue"
    assert checkpoint_status(date(2026, 6, 2), today=date(2026, 6, 2)) == "Due"
    assert checkpoint_status(date(2026, 6, 10), today=date(2026, 6, 2)) == "Due Soon"
    assert checkpoint_status(date(2026, 7, 1), today=date(2026, 6, 2)) == "Not Due"


def create_test_batch(production_date):
    product = Product(name="Toasted Cherry Simple Syrup", code="TC-SYR")
    recipe = Recipe(
        product=product,
        name="Toasted Cherry Simple Syrup",
        version="1",
        procedure_text="Procedure",
    )
    recipe.ingredients.append(
        RecipeIngredient(
            ingredient_name="Sugar",
            default_quantity=37.5,
            default_unit="lb",
            sort_order=1,
        )
    )
    db.session.add(product)
    db.session.commit()
    return create_batch(product.id, recipe.id, production_date)
