from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    __table_args__ = (
        CheckConstraint(
            "stock >= 0",
            name="ck_inventory_stock_nonnegative",
        ),
        CheckConstraint(
            "length(trim(product)) > 0",
            name="ck_inventory_product_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    product: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )