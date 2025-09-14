"""
TECHGURU ElevateCRM Development API Endpoints

Development-only API endpoints for testing and data seeding.
Only available when ENVIRONMENT=development.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from app.core.config import settings
from app.core.dependencies import get_async_session
from app.scripts.seed_data import seed_database

logger = logging.getLogger(__name__)

# Create router for development endpoints
router = APIRouter(prefix="/dev", tags=["Development"])


def check_development_mode():
    """Dependency to ensure endpoints only work in development"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Development endpoints not available in production"
        )


@router.get("/health")
async def dev_health():
    """Development health check endpoint"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "message": "Development API is available"
    }


@router.post("/seed")
async def run_seeder(
    _: None = Depends(check_development_mode),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Run the database seeder to populate development data.
    
    This endpoint:
    - Creates demo company, users, contacts, and products
    - Is idempotent (safe to run multiple times)
    - Only available in development mode
    
    Returns:
        dict: Seeding results and demo login information
    """
    try:
        logger.info("Starting database seeding...")
        
        success = await seed_database()
        
        if success:
            return {
                "status": "success",
                "message": "Database seeding completed successfully",
                "demo_info": {
                    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                    "admin_email": "admin@techguru.com",
                    "company_name": "TECHGURU Demo Company"
                },
                "instructions": {
                    "frontend_login": "Use Keycloak at http://localhost:8080",
                    "api_testing": "Use X-Tenant-ID header with the tenant_id above",
                    "endpoints": [
                        "GET /api/v1/contacts",
                        "GET /api/v1/products",
                        "GET /health"
                    ]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database seeding failed"
            )
            
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}"
        )


@router.delete("/seed")
async def clear_seed_data(
    _: None = Depends(check_development_mode),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Clear all seeded development data.
    
    WARNING: This will delete all data for the demo tenant!
    Only available in development mode.
    
    Returns:
        dict: Clearing results
    """
    try:
        from app.models import Company, User, Contact, Product, Order, Integration
        from sqlalchemy import delete
        
        logger.warning("Clearing all seed data...")
        
        # Delete in reverse dependency order
        demo_tenant_id = "550e8400-e29b-41d4-a716-446655440000"
        
        await db.execute(delete(Order).where(Order.company_id == demo_tenant_id))
        await db.execute(delete(Integration).where(Integration.company_id == demo_tenant_id))
        await db.execute(delete(Product).where(Product.company_id == demo_tenant_id))
        await db.execute(delete(Contact).where(Contact.company_id == demo_tenant_id))
        await db.execute(delete(User).where(User.company_id == demo_tenant_id))
        await db.execute(delete(Company).where(Company.id == demo_tenant_id))
        
        await db.commit()
        
        logger.info("Seed data cleared successfully")
        
        return {
            "status": "success",
            "message": "All seed data cleared successfully",
            "cleared_tenant": demo_tenant_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing seed data: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear seed data: {str(e)}"
        )


@router.get("/info")
async def dev_info(
    _: None = Depends(check_development_mode)
):
    """
    Get development environment information.
    
    Returns:
        dict: Development environment details
    """
    return {
        "environment": settings.ENVIRONMENT,
        "database_url": settings.DATABASE_URL.replace(settings.DB_PASSWORD, "****") if settings.DATABASE_URL else None,
        "demo_tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "available_endpoints": [
            "POST /dev/seed - Run database seeder",
            "DELETE /dev/seed - Clear seed data", 
            "GET /dev/info - This endpoint",
            "GET /dev/health - Development health check"
        ],
        "testing_headers": {
            "X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000",
            "Content-Type": "application/json"
        }
    }
