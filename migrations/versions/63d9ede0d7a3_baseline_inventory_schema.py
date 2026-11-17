"""baseline inventory schema

Revision ID: 63d9ede0d7a3
Revises: 
Create Date: 2026-11-18 02:49:31.510370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63d9ede0d7a3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product", sa.String(length=100), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_inventory_items_id",
        "inventory_items",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_items_id",
        table_name="inventory_items",
    )
    op.drop_table("inventory_items")
