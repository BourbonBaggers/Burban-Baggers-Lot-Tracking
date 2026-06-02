from datetime import date

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app.models import Batch, Product, Recipe
from app.services.batches import create_batch, update_batch_ingredients

main = Blueprint("main", __name__)


@main.get("/")
def index():
    recent_batches = Batch.query.order_by(Batch.created_at.desc()).limit(8).all()
    return render_template("index.html", recent_batches=recent_batches)


@main.get("/health")
def health():
    return jsonify({"status": "ok"})


@main.get("/batches")
def batch_list():
    query = request.args.get("q", "").strip()
    batches = Batch.query

    if query:
        batches = batches.filter(Batch.lot_number.contains(query))

    batches = batches.order_by(Batch.production_date.desc(), Batch.id.desc()).all()
    return render_template("batches/list.html", batches=batches, query=query)


@main.get("/batches/new")
def new_batch():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    recipes = Recipe.query.filter_by(active=True).order_by(Recipe.version.desc()).all()
    return render_template(
        "batches/new.html",
        products=products,
        recipes=recipes,
        today=date.today().isoformat(),
    )


@main.get("/batches/<lot_number>")
def batch_detail(lot_number):
    batch = Batch.query.filter_by(lot_number=lot_number).first_or_404()
    return render_template("batches/detail.html", batch=batch)


@main.post("/api/batches")
def api_create_batch():
    try:
        payload = request.get_json(force=True)
        production_date = date.fromisoformat(payload["production_date"])
        batch = create_batch(
            product_id=int(payload["product_id"]),
            recipe_id=int(payload["recipe_id"]),
            production_date=production_date,
            lot_number=payload.get("lot_number") or None,
            notes=payload.get("notes", ""),
        )
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    location = url_for("main.batch_detail", lot_number=batch.lot_number)
    return jsonify({"id": batch.id, "lot_number": batch.lot_number, "location": location}), 201


@main.patch("/api/batches/<int:batch_id>/ingredients")
def api_update_batch_ingredients(batch_id):
    try:
        payload = request.get_json(force=True)
        batch = update_batch_ingredients(batch_id, payload.get("ingredients", []))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": batch.id, "lot_number": batch.lot_number})
