from datetime import datetime, timezone

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    code = db.Column(db.String(40), nullable=False, unique=True, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    recipes = db.relationship("Recipe", back_populates="product")
    batches = db.relationship("Batch", back_populates="product")


class Recipe(TimestampMixin, db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    version = db.Column(db.String(40), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    target_ph = db.Column(db.Numeric(5, 2))
    target_brix = db.Column(db.Numeric(5, 2))
    target_hot_fill_temp_f = db.Column(db.Integer)
    expected_yield = db.Column(db.String(80))
    procedure_text = db.Column(db.Text, nullable=False, default="")
    notes = db.Column(db.Text, nullable=False, default="")

    product = db.relationship("Product", back_populates="recipes")
    ingredients = db.relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.sort_order",
    )
    batches = db.relationship("Batch", back_populates="recipe")

    __table_args__ = (
        db.UniqueConstraint("product_id", "version", name="uq_recipe_product_version"),
    )


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    ingredient_name = db.Column(db.String(160), nullable=False)
    default_quantity = db.Column(db.Numeric(12, 3), nullable=False)
    default_unit = db.Column(db.String(40), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=False, default="")

    recipe = db.relationship("Recipe", back_populates="ingredients")


class Batch(TimestampMixin, db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    lot_number = db.Column(db.String(80), nullable=False, unique=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="Draft", index=True)
    notes = db.Column(db.Text, nullable=False, default="")

    product = db.relationship("Product", back_populates="batches")
    recipe = db.relationship("Recipe", back_populates="batches")
    ingredients = db.relationship(
        "BatchIngredient",
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    production_record = db.relationship(
        "ProductionRecord",
        back_populates="batch",
        cascade="all, delete-orphan",
        uselist=False,
    )
    bottle_count = db.relationship(
        "BottleCount",
        back_populates="batch",
        cascade="all, delete-orphan",
        uselist=False,
    )
    qc_records = db.relationship(
        "QCRecord",
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    shelf_life_checkpoints = db.relationship(
        "ShelfLifeCheckpoint",
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    labels = db.relationship(
        "LotLabel",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class BatchIngredient(db.Model):
    __tablename__ = "batch_ingredients"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    ingredient_name = db.Column(db.String(160), nullable=False)
    supplier = db.Column(db.String(160), nullable=False, default="")
    supplier_lot = db.Column(db.String(120), nullable=False, default="")
    internal_lot = db.Column(db.String(120), nullable=False, default="")
    default_quantity = db.Column(db.Numeric(12, 3), nullable=False)
    actual_quantity = db.Column(db.Numeric(12, 3), nullable=False)
    unit = db.Column(db.String(40), nullable=False)
    expiration_date = db.Column(db.Date)
    notes = db.Column(db.Text, nullable=False, default="")

    batch = db.relationship("Batch", back_populates="ingredients")


class ProductionRecord(db.Model):
    __tablename__ = "production_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False,
        unique=True,
    )
    steep_start_time = db.Column(db.DateTime(timezone=True))
    steep_end_time = db.Column(db.DateTime(timezone=True))
    heat_start_time = db.Column(db.DateTime(timezone=True))
    bottling_start_time = db.Column(db.DateTime(timezone=True))
    bottling_end_time = db.Column(db.DateTime(timezone=True))
    bottling_start_temp_f = db.Column(db.Numeric(6, 2))
    bottling_end_temp_f = db.Column(db.Numeric(6, 2))
    notes = db.Column(db.Text, nullable=False, default="")

    batch = db.relationship("Batch", back_populates="production_record")


class BottleCount(db.Model):
    __tablename__ = "bottle_counts"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False,
        unique=True,
    )
    filled_count = db.Column(db.Integer, nullable=False, default=0)
    rejected_count = db.Column(db.Integer, nullable=False, default=0)
    retained_sample_count = db.Column(db.Integer, nullable=False, default=0)
    released_count = db.Column(db.Integer, nullable=False, default=0)
    disposed_count = db.Column(db.Integer, nullable=False, default=0)

    batch = db.relationship("Batch", back_populates="bottle_count")


class QCRecord(TimestampMixin, db.Model):
    __tablename__ = "qc_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    qc_type = db.Column(db.String(40), nullable=False)
    ph = db.Column(db.Numeric(5, 2))
    brix = db.Column(db.Numeric(5, 2))
    measurement_temp_f = db.Column(db.Numeric(6, 2))
    appearance = db.Column(db.Text, nullable=False, default="")
    aroma = db.Column(db.Text, nullable=False, default="")
    taste_notes = db.Column(db.Text, nullable=False, default="")
    seal_condition = db.Column(db.Text, nullable=False, default="")
    spoilage_observed = db.Column(db.Boolean, nullable=False, default=False)
    passed = db.Column(db.Boolean)
    notes = db.Column(db.Text, nullable=False, default="")

    batch = db.relationship("Batch", back_populates="qc_records")


class ShelfLifeCheckpoint(TimestampMixin, db.Model):
    __tablename__ = "shelf_life_checkpoints"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    checkpoint_month = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, default="Not Due", index=True)
    inspection_date = db.Column(db.Date)
    ph = db.Column(db.Numeric(5, 2))
    brix = db.Column(db.Numeric(5, 2))
    appearance = db.Column(db.Text, nullable=False, default="")
    aroma = db.Column(db.Text, nullable=False, default="")
    taste_notes = db.Column(db.Text, nullable=False, default="")
    seal_condition = db.Column(db.Text, nullable=False, default="")
    spoilage_observations = db.Column(db.Text, nullable=False, default="")
    passed = db.Column(db.Boolean)
    notes = db.Column(db.Text, nullable=False, default="")

    batch = db.relationship("Batch", back_populates="shelf_life_checkpoints")

    __table_args__ = (
        db.UniqueConstraint(
            "batch_id",
            "checkpoint_month",
            name="uq_checkpoint_batch_month",
        ),
    )


class LotLabel(TimestampMixin, db.Model):
    __tablename__ = "lot_labels"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    barcode_png_path = db.Column(db.String(500), nullable=False)

    batch = db.relationship("Batch", back_populates="labels")
