from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient
from app.services.batches import create_batch
from app.services.labels import label_expiration_date
from app.services.production import (
    update_batch_status,
    update_bottle_count,
    update_release_qc,
)


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


def test_create_batch_copies_recipe_ingredients(app_context):
    product, recipe = create_test_recipe()

    batch = create_batch(
        product_id=product.id,
        recipe_id=recipe.id,
        production_date=date(2026, 6, 2),
    )

    assert batch.lot_number == "TC-SYR-20260602-A"
    assert len(batch.ingredients) == 1
    assert batch.ingredients[0].ingredient_name == "Sugar"
    assert batch.ingredients[0].actual_quantity == batch.ingredients[0].default_quantity


def test_update_bottle_count_calculates_released_count(app_context):
    product, recipe = create_test_recipe()
    batch = create_batch(product.id, recipe.id, date(2026, 6, 2))

    count = update_bottle_count(
        batch.id,
        {
            "filled_count": "120",
            "rejected_count": "5",
            "retained_sample_count": "4",
            "disposed_count": "1",
        },
    )

    assert count.released_count == 110


def test_release_qc_and_status_update(app_context):
    product, recipe = create_test_recipe()
    batch = create_batch(product.id, recipe.id, date(2026, 6, 2))

    qc = update_release_qc(
        batch.id,
        {
            "ph": "3.33",
            "brix": "52",
            "measurement_temp_f": "72",
            "spoilage_observed": "false",
            "passed": "true",
            "appearance": "Clear",
            "aroma": "Cherry",
            "taste_notes": "Balanced",
            "seal_condition": "Good",
            "notes": "Release check",
        },
    )
    updated_batch = update_batch_status(batch.id, "Released")

    assert qc.passed is True
    assert updated_batch.status == "Released"


def test_label_expiration_uses_product_shelf_life(app_context):
    product, recipe = create_test_recipe()
    product.shelf_life_months = 12
    db.session.commit()
    batch = create_batch(product.id, recipe.id, date(2026, 6, 2))

    assert label_expiration_date(batch) == date(2027, 6, 2)


def create_test_recipe():
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
    return product, recipe
