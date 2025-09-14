"""
TECHGURU ElevateCRM - FastAPI Application Entry Point
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.v1.api import api_router
from app.api.v1.health import router as health_router
from app.middleware.tenant import TenantMiddleware
from app.middleware.security import SecurityMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting TECHGURU ElevateCRM API...")       

    # Create database tables
    await create_tables()
    logger.info("Database tables created/verified")

    # Initialize real-time service
    try:
        from app.services.realtime_service import realtime_service
        await realtime_service.connect()
        logger.info("✅ Real-time service (Redis) connected")
    except Exception as e:
        logger.warning(f"⚠️ Real-time service failed to connect: {e}")
        logger.warning("Real-time features will be disabled")

    yield

    # Cleanup real-time service
    try:
        from app.services.realtime_service import realtime_service
        await realtime_service.disconnect()
        logger.info("Real-time service disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting real-time service: {e}")

    logger.info("Shutting down TECHGURU ElevateCRM API...")
# Create FastAPI app
app = FastAPI(
    title="TECHGURU ElevateCRM",
    description="Modern CRM + Inventory Management Platform",
    version=os.getenv("BUILD_VERSION", "0.1.0-dev"),
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(TenantMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "techguru-elevatecrm-api",
        "version": os.getenv("BUILD_VERSION", "0.1.0-dev"),
        "environment": settings.ENVIRONMENT
    }

# Version endpoint
@app.get("/version")
async def version():
    """Version endpoint"""
    return {
        "version": os.getenv("BUILD_VERSION", "0.1.0-dev"),
        "service": "techguru-elevatecrm-api"
    }

# Development endpoints (only in debug mode)
if settings.DEBUG:
    @app.get("/dev/seed", tags=["Development"])
    async def seed_database_endpoint():
        """Seed database with demo data (development only)"""
        try:
            from app.scripts.seed_data import seed_database
            success = await seed_database()
            if success:
                return {"status": "success", "message": "Database seeded successfully"}
            else:
                return {"status": "error", "message": "Failed to seed database"}
        except Exception as e:
            logger.error(f"Seeding failed: {e}", exc_info=True)
            return {"status": "error", "message": f"Seeding failed: {str(e)}"}

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(api_router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
