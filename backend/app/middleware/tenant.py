"""
TECHGURU ElevateCRM Tenant Middleware

Handles multi-tenant request context and data isolation.
SQLite-compatible implementation using application-level filtering.
"""
import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.tenant_context import TenantContextManager

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to handle tenant context for multi-tenant requests"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and set tenant context"""
        
        # Skip tenant context for health checks and static files
        if request.url.path in ["/healthz", "/version", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        if request.url.path.startswith("/static/"):
            return await call_next(request)

        tenant_id = None
        user_profile = None
        
        try:
            # Try to extract tenant ID from various sources
            tenant_id, user_profile = await self._extract_tenant_id(request)
            
            if tenant_id:
                # Set tenant context in request state AND application context
                request.state.tenant_id = tenant_id
                request.state.user = user_profile  # Store user for other middleware/handlers
                
                # Set application-level tenant context (SQLite compatible)
                TenantContextManager.set_tenant_id(tenant_id)
                
                logger.debug(f"Set tenant context: {tenant_id}")
            else:
                # Clear tenant context if no tenant found
                TenantContextManager.clear_tenant_id()
                logger.debug("No tenant ID found in request")
                
        except Exception as e:
            logger.warning(f"Failed to extract tenant ID: {e}")
        
        # Continue with request processing
        response = await call_next(request)
        
        # Add tenant ID to response headers for debugging (if present)
        if tenant_id:
            response.headers["X-Tenant-ID"] = str(tenant_id)
            
        return response

    async def _extract_tenant_id(self, request: Request) -> tuple[Optional[str], Optional[object]]:
        """
        Extract tenant ID from request
        
        Tries multiple methods:
        1. JWT token claims (preferred)
        2. X-Tenant-ID header
        3. Subdomain (if applicable) 
        4. Query parameter
        
        Returns:
            Tuple of (tenant_id, user_profile)
        """
        
        # Method 1: Extract from JWT token (preferred method)
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            try:
                from app.core.auth import extract_bearer_token, validate_jwt_token
                
                token = extract_bearer_token(authorization)
                user_profile = await validate_jwt_token(token)
                
                if user_profile.company_id:
                    logger.debug(f"Found tenant ID in JWT: {user_profile.company_id}")
                    return user_profile.company_id, user_profile
                    
            except Exception as e:
                logger.debug(f"Failed to extract tenant from JWT: {e}")
        
        # Method 2: Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            logger.debug(f"Found tenant ID in header: {tenant_id}")
            return tenant_id, None
        
        # Method 3: Extract from subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www" and subdomain != "api":
                logger.debug(f"Found potential tenant subdomain: {subdomain}")
                # Note: This would require a lookup to convert subdomain to tenant_id
                # For now, we'll skip this method in favor of explicit tenant IDs
        
        # Method 4: Check query parameter
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            logger.debug(f"Found tenant ID in query param: {tenant_id}")
            return tenant_id, None
            
        return None, None
