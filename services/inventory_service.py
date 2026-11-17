from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import InventoryItem
from schemas import InventoryItemCreate


def create_item(db: Session, item: InventoryItemCreate):
    db_item = InventoryItem(
        product=item.product,
        stock=item.stock,
    )

    db.add(db_item)
    commit_changes(db)
    db.refresh(db_item)

    return db_item


def list_items(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
):
    query = select(InventoryItem)

    if search:
        query = query.where(
            InventoryItem.product.ilike(f"%{search}%")
        )

    query = query.order_by(InventoryItem.id)
    query = query.offset(skip).limit(limit)

    return db.scalars(query).all()


def count_items(
    db: Session,
    search: str | None = None,
) -> int:
    query = select(func.count()).select_from(InventoryItem)

    if search:
        query = query.where(
            InventoryItem.product.ilike(f"%{search}%")
        )

    return db.scalar(query) or 0


def get_item(db: Session, item_id: int):
    return db.get(InventoryItem, item_id)


def update_item(
    db: Session,
    item_id: int,
    item: InventoryItemCreate,
):
    db_item = get_item(db, item_id)

    if db_item is None:
        return None

    db_item.product = item.product
    db_item.stock = item.stock

    commit_changes(db)
    db.refresh(db_item)

    return db_item


def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)

    if db_item is None:
        return False

    db.delete(db_item)
    commit_changes(db)

    return True


def get_low_stock_items(db: Session, threshold: int = 5):
    query = (
        select(InventoryItem)
        .where(InventoryItem.stock < threshold)
        .order_by(InventoryItem.stock, InventoryItem.id)
    )

    return db.scalars(query).all()


def commit_changes(db: Session):
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise