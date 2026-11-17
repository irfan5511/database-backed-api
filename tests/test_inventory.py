import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app


@pytest.fixture
def client(tmp_path):
    # Each test receives its own temporary SQLite database.
    database_path = tmp_path / "test_inventory.db"
    test_engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()
        test_engine.dispose()


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item(client):
    response = client.post(
        "/inventory/items",
        json={"product": "Keyboard", "stock": 10},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "product": "Keyboard",
        "stock": 10,
    }


def test_list_items_empty(client):
    response = client.get("/inventory/items")

    assert response.status_code == 200
    assert response.json() == []


def test_list_items(client):
    client.post(
        "/inventory/items",
        json={"product": "Mouse", "stock": 5},
    )
    client.post(
        "/inventory/items",
        json={"product": "Monitor", "stock": 8},
    )

    response = client.get("/inventory/items")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["product"] == "Mouse"
    assert response.json()[1]["product"] == "Monitor"


def test_get_item(client):
    created = client.post(
        "/inventory/items",
        json={"product": "Laptop", "stock": 3},
    ).json()

    response = client.get(
        f"/inventory/items/{created['id']}"
    )

    assert response.status_code == 200
    assert response.json()["product"] == "Laptop"


def test_get_item_not_found(client):
    response = client.get("/inventory/items/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory item not found"


def test_update_item(client):
    created = client.post(
        "/inventory/items",
        json={"product": "Keyboard", "stock": 5},
    ).json()

    response = client.put(
        f"/inventory/items/{created['id']}",
        json={"product": "Mechanical Keyboard", "stock": 20},
    )

    assert response.status_code == 200
    assert response.json()["product"] == "Mechanical Keyboard"
    assert response.json()["stock"] == 20

    # Confirm the updated values were persisted.
    saved = client.get(
        f"/inventory/items/{created['id']}"
    )
    assert saved.json()["stock"] == 20


def test_update_item_not_found(client):
    response = client.put(
        "/inventory/items/999",
        json={"product": "Mouse", "stock": 5},
    )

    assert response.status_code == 404


def test_delete_item(client):
    created = client.post(
        "/inventory/items",
        json={"product": "Webcam", "stock": 4},
    ).json()

    response = client.delete(
        f"/inventory/items/{created['id']}"
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_item_not_found(client):
    response = client.delete("/inventory/items/999")

    assert response.status_code == 404


def test_get_deleted_item(client):
    created = client.post(
        "/inventory/items",
        json={"product": "Headphones", "stock": 2},
    ).json()

    client.delete(f"/inventory/items/{created['id']}")

    response = client.get(
        f"/inventory/items/{created['id']}"
    )

    assert response.status_code == 404


def test_negative_stock_rejected(client):
    response = client.post(
        "/inventory/items",
        json={"product": "Mouse", "stock": -1},
    )

    assert response.status_code == 422


def test_empty_product_rejected(client):
    response = client.post(
        "/inventory/items",
        json={"product": "", "stock": 5},
    )

    assert response.status_code == 422


def test_missing_stock_rejected(client):
    response = client.post(
        "/inventory/items",
        json={"product": "Keyboard"},
    )

    assert response.status_code == 422


def test_filter_items_by_product(client):
    client.post(
        "/inventory/items",
        json={"product": "Apple Keyboard", "stock": 8},
    )
    client.post(
        "/inventory/items",
        json={"product": "Gaming Mouse", "stock": 4},
    )
    client.post(
        "/inventory/items",
        json={"product": "Apple Mouse", "stock": 6},
    )

    response = client.get("/inventory/items?search=mouse")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(
        "mouse" in item["product"].lower()
        for item in response.json()
    )


def test_pagination(client):
    for i in range(5):
        client.post(
            "/inventory/items",
            json={"product": f"Item {i}", "stock": i},
        )

    response = client.get("/inventory/items?skip=2&limit=2")

    assert response.status_code == 200
    assert [item["product"] for item in response.json()] == [
        "Item 2",
        "Item 3",
    ]


def test_invalid_limit(client):
    response = client.get("/inventory/items?limit=0")

    assert response.status_code == 422


def test_negative_skip(client):
    response = client.get("/inventory/items?skip=-1")

    assert response.status_code == 422


def test_low_stock_items(client):
    client.post(
        "/inventory/items",
        json={"product": "Mouse", "stock": 2},
    )
    client.post(
        "/inventory/items",
        json={"product": "Monitor", "stock": 12},
    )
    client.post(
        "/inventory/items",
        json={"product": "Keyboard", "stock": 4},
    )

    response = client.get("/inventory/items/low-stock")

    assert response.status_code == 200
    assert [item["product"] for item in response.json()] == [
        "Mouse",
        "Keyboard",
    ]


def test_custom_low_stock_threshold(client):
    client.post(
        "/inventory/items",
        json={"product": "Laptop", "stock": 7},
    )
    client.post(
        "/inventory/items",
        json={"product": "Webcam", "stock": 3},
    )

    response = client.get(
        "/inventory/items/low-stock?threshold=10"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_low_stock_excludes_threshold_value(client):
    client.post(
        "/inventory/items",
        json={"product": "Keyboard", "stock": 5},
    )

    response = client.get(
        "/inventory/items/low-stock?threshold=5"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_invalid_low_stock_threshold(client):
    response = client.get(
        "/inventory/items/low-stock?threshold=-1"
    )

    assert response.status_code == 422


def test_paginated_response(client):
    for i in range(3):
        client.post(
            "/inventory/items",
            json={"product": f"Item {i}", "stock": i},
        )

    response = client.get(
        "/inventory/items/page?skip=0&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert data["has_next"] is True


def test_last_page(client):
    for i in range(3):
        client.post(
            "/inventory/items",
            json={"product": f"Item {i}", "stock": i},
        )

    response = client.get(
        "/inventory/items/page?skip=2&limit=2"
    )

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 3
    assert data["has_next"] is False


def test_paginated_search(client):
    client.post(
        "/inventory/items",
        json={"product": "Gaming Mouse", "stock": 5},
    )
    client.post(
        "/inventory/items",
        json={"product": "Office Mouse", "stock": 8},
    )
    client.post(
        "/inventory/items",
        json={"product": "Keyboard", "stock": 10},
    )

    response = client.get(
        "/inventory/items/page?search=mouse&limit=1"
    )

    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["has_next"] is True


def test_empty_page(client):
    response = client.get("/inventory/items/page")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "skip": 0,
        "limit": 10,
        "has_next": False,
    }


def test_invalid_page_limit(client):
    response = client.get(
        "/inventory/items/page?limit=101"
    )

    assert response.status_code == 422


def test_whitespace_only_product_rejected(client):
    response = client.post(
        "/inventory/items",
        json={"product": "   ", "stock": 5},
    )

    assert response.status_code == 422


def test_product_whitespace_trimmed(client):
    response = client.post(
        "/inventory/items",
        json={"product": "  Keyboard  ", "stock": 5},
    )

    assert response.status_code == 201
    assert response.json()["product"] == "Keyboard"


def test_update_whitespace_product_rejected(client):
    created = client.post(
        "/inventory/items",
        json={"product": "Mouse", "stock": 5},
    ).json()

    response = client.put(
        f"/inventory/items/{created['id']}",
        json={"product": "   ", "stock": 10},
    )

    assert response.status_code == 422

    saved = client.get(
        f"/inventory/items/{created['id']}"
    )

    assert saved.json()["product"] == "Mouse"
    assert saved.json()["stock"] == 5


def test_database_rejects_negative_stock(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session

    from database import Base
    from models import InventoryItem

    engine = create_engine(
        f"sqlite:///{tmp_path / 'constraints.db'}"
    )
    Base.metadata.create_all(bind=engine)

    try:
        with Session(engine) as db:
            db.add(
                InventoryItem(
                    product="Mouse",
                    stock=-10,
                )
            )

            with pytest.raises(IntegrityError):
                db.commit()

            db.rollback()
    finally:
        engine.dispose()


def test_failed_commit_rolls_back(tmp_path):
    from sqlalchemy import create_engine, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session

    from database import Base
    from models import InventoryItem
    from services.inventory_service import commit_changes

    engine = create_engine(
        f"sqlite:///{tmp_path / 'rollback.db'}"
    )
    Base.metadata.create_all(bind=engine)

    try:
        with Session(engine) as db:
            db.add(
                InventoryItem(
                    product="Invalid",
                    stock=-5,
                )
            )

            with pytest.raises(IntegrityError):
                commit_changes(db)

            assert not db.in_transaction()

            # Confirm that the session works after rollback.
            db.add(
                InventoryItem(
                    product="Valid",
                    stock=10,
                )
            )
            commit_changes(db)

            saved = db.scalars(
                select(InventoryItem)
            ).all()

            assert len(saved) == 1
            assert saved[0].product == "Valid"
    finally:
        engine.dispose()