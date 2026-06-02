"""add core lot tracking schema

Revision ID: de605f321afb
Revises:
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa


revision = "de605f321afb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_products_code"), "products", ["code"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("target_ph", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("target_brix", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("target_hot_fill_temp_f", sa.Integer(), nullable=True),
        sa.Column("expected_yield", sa.String(length=80), nullable=True),
        sa.Column("procedure_text", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "version", name="uq_recipe_product_version"),
    )

    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lot_number", sa.String(length=80), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lot_number"),
    )
    op.create_index(op.f("ix_batches_lot_number"), "batches", ["lot_number"], unique=False)
    op.create_index(op.f("ix_batches_status"), "batches", ["status"], unique=False)

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_name", sa.String(length=160), nullable=False),
        sa.Column("default_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("default_unit", sa.String(length=40), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "batch_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_name", sa.String(length=160), nullable=False),
        sa.Column("supplier", sa.String(length=160), nullable=False),
        sa.Column("supplier_lot", sa.String(length=120), nullable=False),
        sa.Column("internal_lot", sa.String(length=120), nullable=False),
        sa.Column("default_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("actual_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "production_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("steep_start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("steep_end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heat_start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bottling_start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bottling_end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bottling_start_temp_f", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("bottling_end_temp_f", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id"),
    )

    op.create_table(
        "bottle_counts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("filled_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("retained_sample_count", sa.Integer(), nullable=False),
        sa.Column("released_count", sa.Integer(), nullable=False),
        sa.Column("disposed_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id"),
    )

    op.create_table(
        "qc_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("qc_type", sa.String(length=40), nullable=False),
        sa.Column("ph", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("brix", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("measurement_temp_f", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("appearance", sa.Text(), nullable=False),
        sa.Column("aroma", sa.Text(), nullable=False),
        sa.Column("taste_notes", sa.Text(), nullable=False),
        sa.Column("seal_condition", sa.Text(), nullable=False),
        sa.Column("spoilage_observed", sa.Boolean(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "shelf_life_checkpoints",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("checkpoint_month", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("inspection_date", sa.Date(), nullable=True),
        sa.Column("ph", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("brix", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("appearance", sa.Text(), nullable=False),
        sa.Column("aroma", sa.Text(), nullable=False),
        sa.Column("taste_notes", sa.Text(), nullable=False),
        sa.Column("seal_condition", sa.Text(), nullable=False),
        sa.Column("spoilage_observations", sa.Text(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id", "checkpoint_month", name="uq_checkpoint_batch_month"),
    )
    op.create_index(
        op.f("ix_shelf_life_checkpoints_due_date"),
        "shelf_life_checkpoints",
        ["due_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_shelf_life_checkpoints_status"),
        "shelf_life_checkpoints",
        ["status"],
        unique=False,
    )

    op.create_table(
        "lot_labels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("barcode_png_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("lot_labels")
    op.drop_index(op.f("ix_shelf_life_checkpoints_status"), table_name="shelf_life_checkpoints")
    op.drop_index(op.f("ix_shelf_life_checkpoints_due_date"), table_name="shelf_life_checkpoints")
    op.drop_table("shelf_life_checkpoints")
    op.drop_table("qc_records")
    op.drop_table("bottle_counts")
    op.drop_table("production_records")
    op.drop_table("batch_ingredients")
    op.drop_table("recipe_ingredients")
    op.drop_index(op.f("ix_batches_status"), table_name="batches")
    op.drop_index(op.f("ix_batches_lot_number"), table_name="batches")
    op.drop_table("batches")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_products_code"), table_name="products")
    op.drop_table("products")
