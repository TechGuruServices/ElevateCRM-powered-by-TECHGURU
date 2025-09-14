"""
TECHGURU ElevateCRM Search API Endpoints

Advanced search endpoints with caching, rate limiting, and tenant isolation.
Supports full-text search, faceted filtering, and intelligent pagination.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
import redis.asyncio as redis
from pydantic import BaseModel, Field

from app.core.dependencies import get_async_db, get_current_user, get_current_tenant_context
from app.core.tenant_context import TenantContext
from app.models.user import User
from app.models.contact import Contact
from app.models.product import Product
from app.services.search_service import SearchService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis client for caching and rate limiting
redis_client = None


async def get_redis_client():
    """Get Redis client for caching"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            await redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available for search caching: {e}")
            redis_client = None
    return redis_client


class SearchResponse(BaseModel):
    """Search API response model"""
    results: List[Dict[str, Any]]
    total: int
    page: int
    limit: int
    cursor: Optional[str] = None
    facets: Dict[str, Dict[str, Any]]
    query_time_ms: Optional[float] = None
    cached: bool = False


class ContactSearchResult(BaseModel):
    """Contact search result model"""
    id: str
    name: str
    email: Optional[str]
    company: Optional[str]
    status: str
    tags: List[str] = []
    phone: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductSearchResult(BaseModel):
    """Product search result model"""
    id: str
    sku: str
    name: str
    category: Optional[str]
    price: Optional[float]
    stock_quantity: int = 0
    low_stock_threshold: int = 10
    brand: Optional[str]
    updated_at: datetime
    is_low_stock: bool = False
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_stock_status(cls, product: Product):
        """Create result with computed stock status"""
        data = cls.from_orm(product)
        data.is_low_stock = product.stock_quantity < product.low_stock_threshold
        return data


async def check_rate_limit(request: Request, user: User, endpoint: str = "search") -> bool:
    """Check rate limit for search endpoints"""
    redis_conn = await get_redis_client()
    if not redis_conn:
        return True  # Allow if Redis unavailable
    
    # Create rate limit key
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"rate_limit:{endpoint}:{user.id}:{client_ip}"
    
    # Rate limit: 100 requests per minute per user per IP
    limit = 100
    window = 60
    
    try:
        # Get current count
        current = await redis_conn.get(rate_key)
        if current is None:
            # First request in window
            await redis_conn.setex(rate_key, window, 1)
            return True
        elif int(current) < limit:
            # Increment counter
            await redis_conn.incr(rate_key)
            return True
        else:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for user {user.id} from {client_ip}")
            return False
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Allow on error


async def get_cached_search_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached search result"""
    redis_conn = await get_redis_client()
    if not redis_conn:
        return None
    
    try:
        cached = await redis_conn.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Cache retrieval failed: {e}")
    
    return None


async def cache_search_result(cache_key: str, result: Dict[str, Any], ttl: int = 60):
    """Cache search result with TTL"""
    redis_conn = await get_redis_client()
    if not redis_conn:
        return
    
    try:
        # Cache for short TTL to balance performance vs freshness
        await redis_conn.setex(cache_key, ttl, json.dumps(result, default=str))
    except Exception as e:
        logger.error(f"Cache storage failed: {e}")


def normalize_search_params(q: str, filters: str, sort: str, page: int, limit: int) -> Dict[str, Any]:
    """Normalize search parameters for caching"""
    # Parse and normalize filters
    try:
        filters_dict = json.loads(filters) if filters else {}
    except (json.JSONDecodeError, TypeError):
        filters_dict = {}
    
    return {
        'q': q.strip() if q else '',
        'filters': filters_dict,
        'sort': sort.strip() if sort else '',
        'page': max(1, page),
        'limit': min(max(1, limit), 100)  # Enforce reasonable limits
    }


@router.get("/contacts", response_model=SearchResponse)
async def search_contacts(
    request: Request,
    q: str = Query("", description="Search query with support for phrases and exclusions"),
    filters: str = Query("", description="JSON filters object"),
    sort: str = Query("", description="Sort fields (comma-separated, prefix with - for desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    no_cache: bool = Query(False, description="Bypass cache"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_current_tenant_context)
):
    """
    Search contacts with full-text search and faceted filtering
    
    **Query Examples:**
    - Simple: `q=john`
    - Phrase: `q="John Smith"`
    - Exclusion: `q=john -smith`
    - Complex: `q="acme corp" software -competitor`
    
    **Filter Examples:**
    - Status: `filters={"status":["active","lead"]}`
    - Tags: `filters={"tags":["vip","partner"]}`
    - Date range: `filters={"created_at":{"from":"2025-01-01","to":"2025-12-31"}}`
    
    **Sort Examples:**
    - By name: `sort=name`
    - By update (desc): `sort=-updated_at`
    - Multi-field: `sort=-updated_at,name`
    """
    start_time = datetime.now()
    
    # Check rate limit
    if not await check_rate_limit(request, current_user, "contacts"):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Normalize parameters
    params = normalize_search_params(q, filters, sort, page, limit)
    
    # Generate cache key
    cache_key = f"search:contacts:{tenant_context.company_id}:" + \
                json.dumps(params, sort_keys=True)
    
    # Check cache if not bypassed
    cached_result = None
    if not no_cache:
        cached_result = await get_cached_search_result(cache_key)
        if cached_result:
            cached_result['cached'] = True
            cached_result['query_time_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            return SearchResponse(**cached_result)
    
    try:
        # Perform search
        search_service = SearchService(db, tenant_context)
        result = await search_service.search_contacts(
            q=params['q'],
            filters=params['filters'],
            sort=params['sort'],
            page=params['page'],
            limit=params['limit']
        )
        
        # Convert ORM objects to response models
        contact_results = []
        for contact in result['results']:
            contact_data = ContactSearchResult.from_orm(contact)
            contact_results.append(contact_data.dict())
        
        # Build response
        response_data = {
            'results': contact_results,
            'total': result['total'],
            'page': result['page'],
            'limit': result['limit'],
            'cursor': None,  # TODO: Implement cursor pagination
            'facets': result.get('facets', {}),
            'query_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'cached': False
        }
        
        # Cache result
        if not no_cache:
            await cache_search_result(cache_key, response_data, ttl=60)
        
        return SearchResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Contact search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search temporarily unavailable")


@router.get("/products", response_model=SearchResponse)
async def search_products(
    request: Request,
    q: str = Query("", description="Search query with support for phrases and exclusions"),
    filters: str = Query("", description="JSON filters object"),
    sort: str = Query("", description="Sort fields (comma-separated, prefix with - for desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    no_cache: bool = Query(False, description="Bypass cache"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_current_tenant_context)
):
    """
    Search products with full-text search and faceted filtering
    
    **Query Examples:**
    - Simple: `q=laptop`
    - SKU search: `q=SKU123`
    - Brand + category: `q=dell laptop`
    - Exclusion: `q=laptop -refurbished`
    
    **Filter Examples:**
    - Category: `filters={"category":["electronics","computers"]}`
    - Price range: `filters={"price":{"gte":100,"lte":1000}}`
    - Stock status: `filters={"stock_quantity":{"gt":0}}`
    - Low stock only: `filters={"stock_status":["low_stock"]}`
    
    **Sort Examples:**
    - By price: `sort=price`
    - By stock (desc): `sort=-stock_quantity`
    - By relevance: `sort=` (default)
    """
    start_time = datetime.now()
    
    # Check rate limit
    if not await check_rate_limit(request, current_user, "products"):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Normalize parameters
    params = normalize_search_params(q, filters, sort, page, limit)
    
    # Generate cache key
    cache_key = f"search:products:{tenant_context.company_id}:" + \
                json.dumps(params, sort_keys=True)
    
    # Check cache if not bypassed
    cached_result = None
    if not no_cache:
        cached_result = await get_cached_search_result(cache_key)
        if cached_result:
            cached_result['cached'] = True
            cached_result['query_time_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            return SearchResponse(**cached_result)
    
    try:
        # Perform search
        search_service = SearchService(db, tenant_context)
        result = await search_service.search_products(
            q=params['q'],
            filters=params['filters'],
            sort=params['sort'],
            page=params['page'],
            limit=params['limit']
        )
        
        # Convert ORM objects to response models
        product_results = []
        for product in result['results']:
            product_data = ProductSearchResult.from_orm_with_stock_status(product)
            product_results.append(product_data.dict())
        
        # Build response
        response_data = {
            'results': product_results,
            'total': result['total'],
            'page': result['page'],
            'limit': result['limit'],
            'cursor': None,  # TODO: Implement cursor pagination
            'facets': result.get('facets', {}),
            'query_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'cached': False
        }
        
        # Cache result
        if not no_cache:
            await cache_search_result(cache_key, response_data, ttl=60)
        
        return SearchResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Product search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search temporarily unavailable")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial query for suggestions"),
    entity: str = Query("contacts", regex="^(contacts|products)$", description="Entity type"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_current_tenant_context)
):
    """Get search suggestions based on partial query"""
    
    # Simple suggestions based on existing data
    suggestions = []
    
    try:
        if entity == "contacts":
            # Get name and company suggestions
            from sqlalchemy import select, func, distinct
            
            # Name suggestions
            name_query = select(distinct(Contact.name)).where(
                and_(
                    Contact.company_id == tenant_context.company_id,
                    Contact.name.ilike(f"{q}%")
                )
            ).limit(limit)
            
            result = await db.execute(name_query)
            names = [row[0] for row in result.fetchall() if row[0]]
            suggestions.extend([{"type": "name", "value": name} for name in names])
            
            # Company suggestions
            if len(suggestions) < limit:
                company_query = select(distinct(Contact.company)).where(
                    and_(
                        Contact.company_id == tenant_context.company_id,
                        Contact.company.ilike(f"{q}%"),
                        Contact.company.isnot(None)
                    )
                ).limit(limit - len(suggestions))
                
                result = await db.execute(company_query)
                companies = [row[0] for row in result.fetchall() if row[0]]
                suggestions.extend([{"type": "company", "value": company} for company in companies])
        
        elif entity == "products":
            # Get product name and SKU suggestions
            from sqlalchemy import select, distinct
            
            # Product name suggestions
            name_query = select(distinct(Product.name)).where(
                and_(
                    Product.company_id == tenant_context.company_id,
                    Product.name.ilike(f"{q}%")
                )
            ).limit(limit)
            
            result = await db.execute(name_query)
            names = [row[0] for row in result.fetchall() if row[0]]
            suggestions.extend([{"type": "name", "value": name} for name in names])
            
            # SKU suggestions
            if len(suggestions) < limit:
                sku_query = select(distinct(Product.sku)).where(
                    and_(
                        Product.company_id == tenant_context.company_id,
                        Product.sku.ilike(f"{q}%")
                    )
                ).limit(limit - len(suggestions))
                
                result = await db.execute(sku_query)
                skus = [row[0] for row in result.fetchall() if row[0]]
                suggestions.extend([{"type": "sku", "value": sku} for sku in skus])
        
        return {
            "suggestions": suggestions[:limit],
            "query": q,
            "entity": entity
        }
        
    except Exception as e:
        logger.error(f"Suggestions failed: {e}")
        return {"suggestions": [], "query": q, "entity": entity}


@router.get("/stats")
async def get_search_stats(
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_current_tenant_context)
):
    """Get search statistics and health info"""
    
    # Check Redis connectivity
    redis_status = "unavailable"
    try:
        redis_conn = await get_redis_client()
        if redis_conn:
            await redis_conn.ping()
            redis_status = "connected"
    except Exception:
        pass
    
    return {
        "search_service": "operational",
        "cache_status": redis_status,
        "supported_entities": ["contacts", "products"],
        "features": {
            "full_text_search": True,
            "fuzzy_matching": True,
            "faceted_search": True,
            "phrase_search": True,
            "exclusion_search": True,
            "caching": redis_status == "connected",
            "rate_limiting": redis_status == "connected"
        },
        "tenant_id": tenant_context.company_id
    }