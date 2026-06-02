from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import Batch, BatchIngredient, Product, Recipe


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


def create_batch(product_id, recipe_id, production_date, lot_number=None, notes=""):
    product = db.session.get(Product, product_id)
    recipe = db.session.get(Recipe, recipe_id)

    if product is None:
        raise ValueError("Product not found")
    if recipe is None or recipe.product_id != product.id:
        raise ValueError("Recipe not found for product")

    lot_number = lot_number or generate_lot_number(product.code, production_date)
    batch = Batch(
        lot_number=lot_number,
        product=product,
        recipe=recipe,
        production_date=production_date,
        status="Draft",
        notes=notes,
    )
    db.session.add(batch)
    db.session.flush()

    for recipe_ingredient in recipe.ingredients:
        db.session.add(
            BatchIngredient(
                batch=batch,
                ingredient_name=recipe_ingredient.ingredient_name,
                default_quantity=recipe_ingredient.default_quantity,
                actual_quantity=recipe_ingredient.default_quantity,
                unit=recipe_ingredient.default_unit,
                notes=recipe_ingredient.notes,
            )
        )

    db.session.commit()
    return batch


def update_batch_ingredients(batch_id, ingredient_updates):
    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")

    ingredients_by_id = {ingredient.id: ingredient for ingredient in batch.ingredients}

    for update in ingredient_updates:
        ingredient_id = int(update["id"])
        ingredient = ingredients_by_id.get(ingredient_id)
        if ingredient is None:
            raise ValueError("Batch ingredient not found")

        ingredient.supplier = update.get("supplier", "").strip()
        ingredient.supplier_lot = update.get("supplier_lot", "").strip()
        ingredient.internal_lot = update.get("internal_lot", "").strip()
        actual_quantity = update.get("actual_quantity")
        ingredient.actual_quantity = (
            Decimal(actual_quantity) if actual_quantity else ingredient.default_quantity
        )
        ingredient.unit = update.get("unit", ingredient.unit).strip()
        expiration_date = update.get("expiration_date")
        ingredient.expiration_date = date.fromisoformat(expiration_date) if expiration_date else None
        ingredient.notes = update.get("notes", "").strip()

    db.session.commit()
    return batch
