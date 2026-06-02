import click

from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient


PROCEDURE_TEXT = """1. Steep infusion bags in water.
2. Add sugar.
3. Add citric acid.
4. Add potassium sorbate.
5. Heat product.
6. Bottle hot.
7. Apply induction seal.
8. Apply shrink band.
9. Record production counts.
10. Perform QC."""


SEED_INGREDIENTS = [
    ("Water", 5, "gallons", "Production water"),
    ("Sugar", 37.5, "lb", ""),
    ("Citric Acid", 57, "g", ""),
    ("Potassium Sorbate", 37.5, "g", ""),
    ("Toasted Cherry Bourbon Baggers teabags", 1, "batch", "Infusion"),
]


def register_cli(app):
    @app.cli.command("seed-data")
    def seed_data():
        seed_initial_data()
        click.echo("Seeded Toasted Cherry Simple Syrup.")


def seed_initial_data():
    product = Product.query.filter_by(code="TC-SYR").one_or_none()
    if product is None:
        product = Product(
            name="Toasted Cherry Simple Syrup",
            code="TC-SYR",
            active=True,
        )
        db.session.add(product)
        db.session.flush()

    recipe = Recipe.query.filter_by(product_id=product.id, version="1").one_or_none()
    if recipe is None:
        recipe = Recipe(
            product=product,
            name="Toasted Cherry Simple Syrup",
            version="1",
            active=True,
            target_ph=3.33,
            target_brix=52,
            target_hot_fill_temp_f=195,
            procedure_text=PROCEDURE_TEXT,
        )
        db.session.add(recipe)
        db.session.flush()

    if not recipe.ingredients:
        for index, ingredient in enumerate(SEED_INGREDIENTS, start=1):
            name, quantity, unit, notes = ingredient
            db.session.add(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_name=name,
                    default_quantity=quantity,
                    default_unit=unit,
                    sort_order=index,
                    notes=notes,
                )
            )

    db.session.commit()
