"""add inventory check constraints

Revision ID: 897abd8c134d
Revises: 63d9ede0d7a3
Create Date: 2026-11-18 02:54:01.776553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '897abd8c134d'
down_revision: Union[str, Sequence[str], None] = '63d9ede0d7a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "inventory_items",
        recreate="always",
    ) as batch_op:
        batch_op.create_check_constraint(
            "ck_inventory_stock_nonnegative",
            "stock >= 0",
        )

        batch_op.create_check_constraint(
            "ck_inventory_product_not_blank",
            "length(trim(product)) > 0",
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "inventory_items",
        recreate="always",
    ) as batch_op:
        batch_op.drop_constraint(
            "ck_inventory_stock_nonnegative",
            type_="check",
        )

        batch_op.drop_constraint(
            "ck_inventory_product_not_blank",
            type_="check",
        )
