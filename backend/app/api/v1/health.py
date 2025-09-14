"""
TECHGURU ElevateCRM Health Check Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import sys
import os

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        dict: Application health status and version
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get("/healthz/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with database connectivity
    
    Args:
        db: Database session
        
    Returns:
        dict: Detailed health information
    """
    health_data = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.DEBUG else "production",
        "python_version": sys.version,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            health_data["checks"]["database"] = "ok"
        else:
            health_data["checks"]["database"] = "error"
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["checks"]["database"] = f"error: {str(e)}"
        health_data["status"] = "degraded"
    
    return health_data