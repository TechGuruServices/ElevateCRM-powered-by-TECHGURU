"""
TECHGURU ElevateCRM Health Check Endpoints
"""
import os
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional
import logging

from app.core.dependencies import get_async_session, get_current_tenant
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Detailed health check endpoint with database connectivity.
    
    Returns system status and component health information.
    """
    database_status = "unknown"
    database_info = {}
    
    try:
        # Test database connectivity
        result = await db.execute(text("SELECT version(), current_database(), current_user"))
        row = result.fetchone()
        if row:
            database_status = "healthy"
            database_info = {
                "version": row[0].split()[0] if row[0] else "unknown",
                "database": row[1],
                "user": row[2]
            }
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        database_status = "unhealthy"
        database_info = {"error": str(e)}

    return {
        "status": "healthy" if database_status == "healthy" else "degraded",
        "service": "techguru-elevatecrm-api",
        "version": settings.BUILD_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": "2025-09-09T09:00:00Z",
        "components": {
            "database": {
                "status": database_status,
                "info": database_info
            },
            "redis": {
                "status": "not_configured",
                "info": "Redis not yet configured"
            },
            "auth": {
                "status": "configured",
                "info": "JWT authentication configured"
            }
        },
        "features": {
            "multi_tenant": True,
            "row_level_security": True,
            "api_versioning": True,
            "development_mode": settings.ENVIRONMENT == "development"
        }
    }


@router.get("/me")
async def get_current_user(
    request: Request,
    tenant_id: str = Depends(get_current_tenant)
) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Returns user profile and tenant context information.
    """
    try:
        # In a full implementation, this would get user from JWT token
        # For now, return tenant information from request state
        user_info = getattr(request.state, 'user', None)
        
        if user_info:
            return {
                "id": getattr(user_info, 'id', 'unknown'),
                "email": getattr(user_info, 'email', 'unknown'),
                "name": f"{getattr(user_info, 'first_name', '')} {getattr(user_info, 'last_name', '')}".strip(),
                "tenant_id": tenant_id,
                "company_id": getattr(user_info, 'company_id', tenant_id),
                "roles": getattr(user_info, 'roles', []),
                "permissions": getattr(user_info, 'permissions', [])
            }
        else:
            # Fallback for development/testing
            return {
                "id": "demo-admin-id",
                "email": "admin@techguru.com",
                "name": "Demo Administrator",
                "tenant_id": tenant_id,
                "company_id": tenant_id,
                "roles": ["admin", "user"],
                "permissions": ["*"]
            }
            
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )
