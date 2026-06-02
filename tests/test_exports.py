from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient
from app.services.batches import create_batch
from app.services.exports import batches_csv, ingredients_csv


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
        seed_batch()
        yield
        db.session.remove()
        db.drop_all()


def test_batch_and_ingredient_exports(app_context):
    batch_response = batches_csv()
    ingredient_response = ingredients_csv()

    assert "TC-SYR-20260602-A" in batch_response.get_data(as_text=True)
    assert "Sugar" in ingredient_response.get_data(as_text=True)


def seed_batch():
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
    create_batch(product.id, recipe.id, date(2026, 6, 2))
