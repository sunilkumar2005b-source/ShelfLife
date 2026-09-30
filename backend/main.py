import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_cursor
from routes import (
    products_router,
    inventory_router,
    sales_router,
    suppliers_router,
    purchase_orders_router,
    weather_router,
    analytics_router,
    ml_router,
    reports_router,
)

# Load environment configuration
env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI application
app = FastAPI(
    title="ShelfLife API",
    description="AI-Powered Perishable Inventory Management and Retail Analytics System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175"
)
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root and Health Endpoints
@app.get("/", tags=["System"])
def home():
    """Root endpoint verifying API availability."""
    return {
        "message": "ShelfLife API is running successfully!",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Verify backend status and PostgreSQL database connection."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return {
            "status": "healthy",
            "backend": "online",
            "database": "connected"
        }
    except Exception as error:
        return {
            "status": "unhealthy",
            "backend": "online",
            "database": "disconnected",
            "error": str(error)
        }


# Mount Modular Routers
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(sales_router)
app.include_router(suppliers_router)
app.include_router(purchase_orders_router)
app.include_router(weather_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(reports_router)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)