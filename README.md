# Database-Backed Inventory API

A RESTful inventory management backend built with Python, FastAPI, SQLAlchemy, SQLite, and Alembic.

The project demonstrates database-backed CRUD operations, request validation, product filtering, pagination, low-stock monitoring, schema migrations, and automated testing.

## Features

- Create, retrieve, update, and delete inventory records
- Persistent SQLite database storage
- SQLAlchemy ORM for database operations
- Pydantic validation for incoming requests
- Product-name filtering
- Offset-based pagination
- Pagination metadata, including total records and `has_next`
- Low-stock inventory detection with configurable thresholds
- Database-level integrity constraints
- Transaction rollback on failed database writes
- Alembic database migrations
- Automated tests using isolated SQLite databases

## Technology Stack

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- Pydantic
- Pytest
- HTTPX
- Uvicorn

## Project Structure

```text
database-backed-api/
├── migrations/
│   ├── versions/
│   └── env.py
├── routers/
│   ├── __init__.py
│   └── inventory.py
├── services/
│   ├── __init__.py
│   └── inventory_service.py
├── tests/
│   └── test_inventory.py
├── alembic.ini
├── database.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository and navigate to the project directory.

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Database Setup

Initialize the database by applying Alembic migrations:

```bash
alembic upgrade head
```

This creates the database schema and applies its integrity constraints.

Database migrations are managed by Alembic rather than automatic SQLAlchemy table creation at application startup.

## Run the Application

```bash
python -m uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Application health response |
| POST | `/inventory/items` | Create inventory item |
| GET | `/inventory/items` | List and filter items |
| GET | `/inventory/items/page` | Paginated inventory response |
| GET | `/inventory/items/low-stock` | Identify low-stock items |
| GET | `/inventory/items/{item_id}` | Retrieve an item |
| PUT | `/inventory/items/{item_id}` | Update an item |
| DELETE | `/inventory/items/{item_id}` | Delete an item |

### Create an Item

Request:

```http
POST /inventory/items
Content-Type: application/json
```

```json
{
  "product": "Keyboard",
  "stock": 10
}
```

Example response:

```json
{
  "id": 1,
  "product": "Keyboard",
  "stock": 10
}
```

### Filter Inventory

```http
GET /inventory/items?search=keyboard
```

### Paginated Inventory

```http
GET /inventory/items/page?skip=0&limit=10
```

The response includes:

- `items`: Inventory records
- `total`: Number of matching records
- `skip`: Number of records skipped
- `limit`: Maximum records requested
- `has_next`: Whether another page is available

### Low-Stock Detection

```http
GET /inventory/items/low-stock?threshold=5
```

Returns items with stock below the specified threshold.

## Data Integrity

The API validates inventory requests using Pydantic.

Additional database constraints prevent:

- Negative stock quantities
- Empty or whitespace-only product names

Database writes use transaction rollback handling to recover from failed commits.

## Automated Testing

Run the test suite:

```bash
python -m pytest -v
```

The project includes 33 automated tests covering CRUD operations, filtering, pagination, validation, low-stock detection, database constraints, and transaction rollback.

Tests run against isolated temporary SQLite databases to protect local inventory records.

## Database Migrations

Review the migration history:

```bash
alembic history
```

Check the current revision:

```bash
alembic current
```

Apply outstanding migrations:

```bash
alembic upgrade head
```

The repository includes an initial schema migration and a subsequent migration that adds inventory integrity constraints.

## Development Notes

The SQLite database and its backups are excluded from version control.
