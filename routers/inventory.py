from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryPageResponse,
)
from services import inventory_service


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/items/page",
    response_model=InventoryPageResponse,
)
def get_inventory_page(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
):
    items = inventory_service.list_items(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
    )

    total = inventory_service.count_items(
        db=db,
        search=search,
    )

    return InventoryPageResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_next=skip + len(items) < total,
    )


@router.post(
    "/items",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(item: InventoryItemCreate, db: DBSession):
    return inventory_service.create_item(db, item)


@router.get(
    "/items",
    response_model=list[InventoryItemResponse],
)
def list_items(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
):
    return inventory_service.list_items(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.get(
    "/items/low-stock",
    response_model=list[InventoryItemResponse],
)
def low_stock_items(
    db: DBSession,
    threshold: int = Query(default=5, ge=0),
):
    return inventory_service.get_low_stock_items(
        db=db,
        threshold=threshold,
    )


@router.get(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
)
def get_item(item_id: int, db: DBSession):
    db_item = inventory_service.get_item(db, item_id)

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found",
        )

    return db_item


@router.put(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
)
def update_item(
    item_id: int,
    item: InventoryItemCreate,
    db: DBSession,
):
    db_item = inventory_service.update_item(db, item_id, item)

    if db_item is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found",
        )

    return db_item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(item_id: int, db: DBSession):
    deleted = inventory_service.delete_item(db, item_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)