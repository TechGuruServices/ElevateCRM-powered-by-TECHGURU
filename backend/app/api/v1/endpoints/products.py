"""
TECHGURU ElevateCRM Products Endpoints
"""
from fastapi import APIRouter, Query, Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Dict, Any, Optional, List
import logging

from app.core.dependencies import get_tenant_db, get_current_tenant
from app.models.product import Product

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_products(
    request: Request,
    response: Response,
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    db: AsyncSession = Depends(get_tenant_db)
) -> Dict[str, Any]:
    """
    List products for current tenant with search, filtering, and pagination.
    
    - **q**: Search query (searches name, SKU, description)
    - **category**: Filter by product category
    - **status**: Filter by product status
    - **limit**: Maximum number of products to return (1-100)
    - **offset**: Number of products to skip for pagination
    
    Returns products with X-Total-Count header for frontend pagination.
    """
    try:
        # Build base query - RLS automatically filters by tenant
        query = select(Product)
        count_query = select(func.count(Product.id))
        
        # Apply search filter if provided
        if q:
            search_filter = or_(
                Product.name.ilike(f"%{q}%"),
                Product.sku.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Apply category filter if provided
        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
            
        # Apply status filter if provided
        if status:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)
        
        # Get total count for X-Total-Count header
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Product.name)
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        products = result.scalars().all()
        
        # Set X-Total-Count header for frontend pagination
        response.headers["X-Total-Count"] = str(total_count)
        
        # Convert to response format
        products_data = []
        for product in products:
            products_data.append({
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "description": product.description,
                "category": product.category,
                "status": product.status,
                "unit_price": float(product.unit_price) if product.unit_price else None,
                "cost_price": float(product.cost_price) if product.cost_price else None,
                "stock_quantity": product.stock_quantity,
                "reorder_level": product.reorder_level,
                "unit_of_measure": product.unit_of_measure,
                "tags": product.tags,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            })
        
        logger.info(f"Retrieved {len(products_data)} products (total: {total_count})")
        
        return {
            "products": products_data,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "query": q,
            "category": category,
            "status": status,
            "has_more": offset + len(products_data) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_tenant_db)
) -> Dict[str, Any]:
    """
    Get a specific product by ID.
    
    Returns product details if found and accessible by current tenant.
    """
    try:
        # Query product by ID - RLS automatically filters by tenant
        query = select(Product).where(Product.id == product_id)
        result = await db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return {
            "id": str(product.id),
            "name": product.name,
            "sku": product.sku,
            "description": product.description,
            "category": product.category,
            "status": product.status,
            "pricing": {
                "unit_price": float(product.unit_price) if product.unit_price else None,
                "cost_price": float(product.cost_price) if product.cost_price else None,
                "currency": "USD"  # From tenant settings
            },
            "inventory": {
                "stock_quantity": product.stock_quantity,
                "reorder_level": product.reorder_level,
                "unit_of_measure": product.unit_of_measure
            },
            "specifications": product.specifications,
            "tags": product.tags,
            "images": product.images,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )
