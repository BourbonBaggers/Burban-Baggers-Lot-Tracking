from decimal import Decimal

from app.extensions import db
from app.models import Product, Recipe, RecipeIngredient


def update_product(product_id, data):
    product = db.session.get(Product, product_id)
    if product is None:
        raise ValueError("Product not found")

    product.name = data["name"].strip()
    product.code = data["code"].strip()
    product.active = parse_bool(data.get("active"))
    db.session.commit()
    return product


def update_recipe(recipe_id, data):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        raise ValueError("Recipe not found")

    recipe.name = data["name"].strip()
    recipe.version = data["version"].strip()
    recipe.active = parse_bool(data.get("active"))
    recipe.target_ph = parse_decimal(data.get("target_ph"))
    recipe.target_brix = parse_decimal(data.get("target_brix"))
    recipe.target_hot_fill_temp_f = parse_int(data.get("target_hot_fill_temp_f"))
    recipe.expected_yield = data.get("expected_yield", "").strip()
    recipe.procedure_text = data.get("procedure_text", "").strip()
    recipe.notes = data.get("notes", "").strip()
    db.session.commit()
    return recipe


def update_recipe_ingredients(recipe_id, ingredient_updates):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        raise ValueError("Recipe not found")

    ingredients_by_id = {ingredient.id: ingredient for ingredient in recipe.ingredients}
    kept_ids = set()

    for index, item in enumerate(ingredient_updates, start=1):
        ingredient_id = item.get("id")
        if ingredient_id:
            ingredient = ingredients_by_id.get(int(ingredient_id))
            if ingredient is None:
                raise ValueError("Recipe ingredient not found")
        else:
            ingredient = RecipeIngredient(recipe=recipe)
            db.session.add(ingredient)

        ingredient.ingredient_name = item["ingredient_name"].strip()
        ingredient.default_quantity = Decimal(item["default_quantity"])
        ingredient.default_unit = item["default_unit"].strip()
        ingredient.sort_order = index
        ingredient.notes = item.get("notes", "").strip()

        if ingredient.id:
            kept_ids.add(ingredient.id)

    for ingredient in list(recipe.ingredients):
        if ingredient.id not in kept_ids and ingredient.id in ingredients_by_id:
            db.session.delete(ingredient)

    db.session.commit()
    return recipe


def parse_decimal(value):
    return Decimal(value) if value else None


def parse_int(value):
    return int(value) if value else None


def parse_bool(value):
    return str(value).lower() in {"true", "1", "yes", "on"}
