import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient
from app.services.recipes import update_product, update_recipe, update_recipe_ingredients


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
        product, recipe = seed_recipe()
        yield product, recipe
        db.session.remove()
        db.drop_all()


def test_update_product_and_recipe(app_context):
    product, recipe = app_context

    update_product(product.id, {"name": "Cherry Syrup", "code": "CH-SYR", "active": "true"})
    update_recipe(
        recipe.id,
        {
            "name": "Cherry Syrup",
            "version": "2",
            "active": "true",
            "target_ph": "3.25",
            "target_brix": "51.5",
            "target_hot_fill_temp_f": "194",
            "expected_yield": "100 bottles",
            "procedure_text": "Updated procedure",
            "notes": "Updated notes",
        },
    )

    assert product.code == "CH-SYR"
    assert recipe.version == "2"
    assert recipe.target_hot_fill_temp_f == 194


def test_update_recipe_ingredients_replaces_defaults(app_context):
    _, recipe = app_context

    update_recipe_ingredients(
        recipe.id,
        [
            {
                "id": str(recipe.ingredients[0].id),
                "ingredient_name": "Sugar",
                "default_quantity": "40",
                "default_unit": "lb",
                "notes": "Updated",
            },
            {
                "id": "",
                "ingredient_name": "Citric Acid",
                "default_quantity": "57",
                "default_unit": "g",
                "notes": "",
            },
        ],
    )

    assert [item.ingredient_name for item in recipe.ingredients] == ["Sugar", "Citric Acid"]
    assert recipe.ingredients[0].default_quantity == 40


def seed_recipe():
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
