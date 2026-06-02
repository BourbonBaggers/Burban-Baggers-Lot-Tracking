from datetime import date

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app.models import Batch, Product, Recipe
from app.services.batches import create_batch, update_batch_ingredients
from app.services.production import (
    update_batch_status,
    update_bottle_count,
    update_production_record,
    update_release_qc,
)

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
    release_qc = next((qc for qc in batch.qc_records if qc.qc_type == "Release"), None)
    return render_template("batches/detail.html", batch=batch, release_qc=release_qc)


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


@main.patch("/api/batches/<int:batch_id>/production")
def api_update_production_record(batch_id):
    try:
        record = update_production_record(batch_id, request.get_json(force=True))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": record.id})


@main.patch("/api/batches/<int:batch_id>/bottle-count")
def api_update_bottle_count(batch_id):
    try:
        count = update_bottle_count(batch_id, request.get_json(force=True))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": count.id, "released_count": count.released_count})


@main.patch("/api/batches/<int:batch_id>/release-qc")
def api_update_release_qc(batch_id):
    try:
        record = update_release_qc(batch_id, request.get_json(force=True))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": record.id})


@main.patch("/api/batches/<int:batch_id>/status")
def api_update_batch_status(batch_id):
    try:
        batch = update_batch_status(batch_id, request.get_json(force=True)["status"])
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"id": batch.id, "status": batch.status})
