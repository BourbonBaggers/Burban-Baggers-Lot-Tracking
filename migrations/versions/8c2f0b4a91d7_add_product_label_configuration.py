"""add product label configuration

Revision ID: 8c2f0b4a91d7
Revises: de605f321afb
Create Date: 2026-06-03
"""

from alembic import op
import sqlalchemy as sa


revision = "8c2f0b4a91d7"
down_revision = "de605f321afb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "products",
        sa.Column("shelf_life_months", sa.Integer(), nullable=False, server_default="12"),
    )
    op.add_column(
        "products",
        sa.Column("barcode_png_path", sa.String(length=500), nullable=False, server_default=""),
    )
    op.execute(
        "UPDATE products SET shelf_life_months = 12, "
        "barcode_png_path = 'barcodes/00850078895011-upc-a-sst1.png' "
        "WHERE code = 'TC-SYR'"
    )


def downgrade():
    op.drop_column("products", "barcode_png_path")
    op.drop_column("products", "shelf_life_months")
