from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient
from app.services.batches import create_batch


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

    batch = create_batch(
        product_id=product.id,
        recipe_id=recipe.id,
        production_date=date(2026, 6, 2),
    )

    assert batch.lot_number == "TC-SYR-20260602-A"
    assert len(batch.ingredients) == 1
    assert batch.ingredients[0].ingredient_name == "Sugar"
    assert batch.ingredients[0].actual_quantity == batch.ingredients[0].default_quantity
