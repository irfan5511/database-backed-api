from fastapi import FastAPI

from routers.inventory import router as inventory_router


app = FastAPI(
    title="Database-Backed Inventory API",
    description="Inventory management using FastAPI, SQLite, SQLAlchemy, and Alembic",
    version="1.0.0",
)

app.include_router(inventory_router)


@app.get("/")
def home():
    return {
        "message": "Database-Backed Inventory API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "sqlite",
    }