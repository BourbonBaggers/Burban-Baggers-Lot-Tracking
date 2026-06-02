from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Batch, LotLabel


def save_lot_label(batch_id, upload, upload_folder):
    batch = db.session.get(Batch, batch_id)
    if batch is None:
        raise ValueError("Batch not found")
    if not upload or not upload.filename:
        raise ValueError("Barcode PNG is required")

    filename = secure_filename(upload.filename)
    if not filename.lower().endswith(".png"):
        raise ValueError("Barcode file must be a PNG")

    label_dir = Path(upload_folder) / "barcodes"
    label_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{batch.lot_number}-{uuid4().hex}.png"
    stored_path = label_dir / stored_name
    upload.save(stored_path)

    label = LotLabel(batch=batch, barcode_png_path=str(stored_path))
    db.session.add(label)
    db.session.commit()
    return label
