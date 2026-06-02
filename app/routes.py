from datetime import date

from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
    url_for,
)

from app.models import Batch, Product, Recipe, ShelfLifeCheckpoint
from app.services.batches import create_batch, update_batch_ingredients
from app.services.checkpoints import (
    batch_to_dict,
    checkpoint_to_dict,
    due_checkpoints,
    refresh_checkpoint_statuses,
    upcoming_checkpoints,
    update_checkpoint,
)
from app.services.exports import batches_csv, checkpoints_csv, ingredients_csv, qc_csv
from app.services.labels import save_lot_label
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
    refresh_checkpoint_statuses(batch.shelf_life_checkpoints)
    release_qc = next((qc for qc in batch.qc_records if qc.qc_type == "Release"), None)
    return render_template("batches/detail.html", batch=batch, release_qc=release_qc)


@main.get("/batches/<lot_number>/label")
def lot_label(lot_number):
    batch = Batch.query.filter_by(lot_number=lot_number).first_or_404()
    label = batch.labels[-1] if batch.labels else None
    return render_template("labels/lot.html", batch=batch, label=label)


@main.get("/labels/<int:label_id>/barcode")
def label_barcode(label_id):
    from app.models import LotLabel

    label = LotLabel.query.get_or_404(label_id)
    return send_file(Path(label.barcode_png_path), mimetype="image/png")


@main.get("/checkpoints")
def checkpoint_list():
    checkpoints = (
        ShelfLifeCheckpoint.query.join(Batch)
        .order_by(ShelfLifeCheckpoint.due_date, ShelfLifeCheckpoint.id)
        .all()
    )
    refresh_checkpoint_statuses(checkpoints)
    return render_template("checkpoints/list.html", checkpoints=checkpoints)


@main.get("/exports/batches.csv")
def export_batches():
    return batches_csv()


@main.get("/exports/ingredients.csv")
def export_ingredients():
    return ingredients_csv()


@main.get("/exports/qc.csv")
def export_qc():
    return qc_csv()


@main.get("/exports/checkpoints.csv")
def export_checkpoints():
    return checkpoints_csv()


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


@main.post("/api/batches/<int:batch_id>/label")
def api_upload_label(batch_id):
    try:
        label = save_lot_label(
            batch_id,
            request.files.get("barcode_png"),
            current_app.config["UPLOAD_FOLDER"],
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    location = url_for("main.lot_label", lot_number=label.batch.lot_number)
    return jsonify({"id": label.id, "location": location}), 201


@main.patch("/api/checkpoints/<int:checkpoint_id>")
def api_update_checkpoint(checkpoint_id):
    try:
        checkpoint = update_checkpoint(checkpoint_id, request.get_json(force=True))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(checkpoint_to_dict(checkpoint))


@main.get("/api/checkpoints/due")
def api_due_checkpoints():
    auth_error = api_auth_error()
    if auth_error:
        return auth_error

    checkpoints = refresh_checkpoint_statuses(due_checkpoints())
    return jsonify({"checkpoints": [checkpoint_to_dict(item) for item in checkpoints]})


@main.get("/api/checkpoints/upcoming")
def api_upcoming_checkpoints():
    auth_error = api_auth_error()
    if auth_error:
        return auth_error

    days = int(request.args.get("days", 30))
    checkpoints = refresh_checkpoint_statuses(upcoming_checkpoints(days=days))
    return jsonify({"checkpoints": [checkpoint_to_dict(item) for item in checkpoints]})


@main.get("/api/batches/<lot_number>")
def api_batch(lot_number):
    auth_error = api_auth_error()
    if auth_error:
        return auth_error

    batch = Batch.query.filter_by(lot_number=lot_number).first_or_404()
    refresh_checkpoint_statuses(batch.shelf_life_checkpoints)
    return jsonify(batch_to_dict(batch))


def api_auth_error():
    api_key = current_app.config.get("API_KEY")
    if not api_key:
        return None

    header_key = request.headers.get("X-API-Key", "")
    bearer = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if api_key in {header_key, bearer}:
        return None

    return jsonify({"error": "Unauthorized"}), 401
