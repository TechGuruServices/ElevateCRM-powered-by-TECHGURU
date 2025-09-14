"""
TECHGURU ElevateCRM - Simplified FastAPI Application Entry Point
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TECHGURU ElevateCRM",
    description="Modern CRM + Inventory Management Platform",
    version=os.getenv("BUILD_VERSION", "0.1.0-dev"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "techguru-elevatecrm-api",
        "version": os.getenv("BUILD_VERSION", "0.1.0-dev"),
        "environment": "development"
    }

# Version endpoint
@app.get("/version")
async def version():
    """Version endpoint"""
    return {
        "version": os.getenv("BUILD_VERSION", "0.1.0-dev"),
        "service": "techguru-elevatecrm-api"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TECHGURU ElevateCRM API is running"}

# Basic API endpoints without authentication for now
@app.get("/api/v1/health")
async def api_health():
    """API health endpoint"""
    return {"status": "healthy", "api_version": "v1"}

@app.get("/api/v1/me")
async def get_me():
    """Get current user info (mock for now)"""
    return {
        "id": "user-123",
        "email": "demo@techguru.com",
        "name": "Demo User",
        "company_id": "company-123",
        "roles": ["user"]
    }

@app.get("/api/v1/contacts")
async def list_contacts():
    """List contacts with basic pagination"""
    return {
        "data": [
            {
                "id": "contact-1", 
                "name": "John Doe", 
                "email": "john@example.com",
                "company": "ACME Corp",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "contact-2", 
                "name": "Jane Smith", 
                "email": "jane@example.com",
                "company": "Tech Solutions",
                "created_at": "2024-01-02T00:00:00Z"
            }
        ],
        "total": 2,
        "limit": 50,
        "offset": 0
    }

@app.get("/api/v1/products")
async def list_products():
    """List products with basic pagination"""
    return {
        "data": [
            {
                "id": "product-1",
                "sku": "LAPTOP-001", 
                "name": "Business Laptop",
                "price": 1299.99,
                "stock_quantity": 25,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "product-2",
                "sku": "MOUSE-001", 
                "name": "Wireless Mouse",
                "price": 49.99,
                "stock_quantity": 150,
                "created_at": "2024-01-02T00:00:00Z"
            }
        ],
        "total": 2,
        "limit": 50,
        "offset": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
