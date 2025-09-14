"""
TECHGURU ElevateCRM Authentication Dependencies

FastAPI dependencies for authentication and authorization.
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import validate_jwt_token, extract_bearer_token, check_user_permissions, UserProfile
from app.core.database import get_async_session
from app.core.tenant_context import TenantContextManager
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserProfile]:
    """
    Get current user from JWT token (optional - returns None if no token)
    
    Args:
        request: FastAPI request object
        credentials: HTTP bearer credentials
        
    Returns:
        Optional[UserProfile]: User profile or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        # Validate JWT token
        user_profile = await validate_jwt_token(credentials.credentials)
        
        # Store user in request state for middleware access
        request.state.user = user_profile
        
        return user_profile
        
    except HTTPException:
        # Token is invalid, but this is optional auth
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Get current authenticated user (required)
    
    Args:
        request: FastAPI request object  
        credentials: HTTP bearer credentials
        
    Returns:
        UserProfile: Authenticated user profile
        
    Raises:
        HTTPException: If not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate JWT token
    user_profile = await validate_jwt_token(credentials.credentials)
    
    # Store user in request state for middleware access
    request.state.user = user_profile
    
    return user_profile


async def get_current_active_user(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Get current active user (email verified)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfile: Active user profile
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    
    return current_user


async def get_current_user_from_db(
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Get current user from database
    
    Args:
        current_user: Current authenticated user profile
        session: Database session
        
    Returns:
        User: User model from database
        
    Raises:
        HTTPException: If user not found in database
    """
    # Query user by external_id (Keycloak sub)
    result = await session.execute(
        select(User).where(User.external_id == current_user.sub)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Try to find by email as fallback
        if current_user.email:
            result = await session.execute(
                select(User).where(User.email == current_user.email)
            )
            user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database. Please contact administrator."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    return user


def require_roles(required_roles: List[str]):
    """
    Dependency factory for role-based access control
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    def role_checker(current_user: UserProfile = Depends(get_current_user)):
        if not check_user_permissions(current_user, required_roles=required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    
    return role_checker


def require_permissions(required_permissions: List[str]):
    """
    Dependency factory for permission-based access control
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Dependency function
    """
    def permission_checker(current_user: UserProfile = Depends(get_current_user)):
        if not check_user_permissions(current_user, required_permissions=required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required permissions: {', '.join(required_permissions)}"
            )
        return current_user
    
    return permission_checker


# Common role dependencies
require_admin = require_roles(["admin"])
require_manager = require_roles(["manager", "admin"])  
require_user = require_roles(["user", "manager", "admin"])


async def get_tenant_from_user(
    current_user: UserProfile = Depends(get_current_user)
) -> str:
    """
    Get tenant ID from current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        str: Tenant/company ID
        
    Raises:
        HTTPException: If user has no company association
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no company association"
        )
    
    try:
        # Validate UUID format
        tenant_id = str(uuid.UUID(current_user.company_id))
        return tenant_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )


# Tenant Database Dependencies
async def get_current_tenant(request: Request) -> str:
    """
    Get current tenant ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Tenant ID (UUID string)
        
    Raises:
        HTTPException: If tenant context is not available
    """
    tenant_id = getattr(request.state, 'tenant_id', None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context not available"
        )
    return tenant_id


async def get_tenant_db(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> AsyncSession:
    """
    Get database session with tenant context set for RLS.
    
    This dependency:
    1. Gets the current tenant ID from request state
    2. Sets the tenant context in the database session using SET LOCAL
    3. Returns the configured session for use in endpoints
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        AsyncSession: Database session with tenant context set
        
    Raises:
        HTTPException: If tenant setup fails
    """
    from sqlalchemy import text
    
    tenant_id = await get_current_tenant(request)
    
    try:
        # Set application-level tenant context (SQLite compatible)
        # This replaces PostgreSQL RLS with application-level filtering
        TenantContextManager.set_tenant_id(tenant_id)
        logger.debug(f"Application tenant context set: {tenant_id}")
        return db
        
    except Exception as e:
        logger.error(f"Failed to set tenant context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tenant context setup error"
        )


# Tenant Context Dependencies
async def get_tenant_context(request: Request) -> str:
    """
    Get the current tenant ID and ensure context is set
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Current tenant ID
        
    Raises:
        HTTPException: If no tenant context is available
    """
    tenant_id = await get_current_tenant(request)
    TenantContextManager.set_tenant_id(tenant_id)
    return tenant_id


def require_tenant_context():
    """
    Dependency that ensures tenant context is available
    
    Returns:
        Function that validates tenant context
    """
    def tenant_validator(tenant_id: str = Depends(get_tenant_context)) -> str:
        return tenant_id
    return tenant_validator
# Database Session Dependencies
async def get_async_db() -> AsyncSession:
    """
    Get database session dependency

    Returns:
        AsyncSession: Database session
    """
    async for session in get_async_session():
        yield session


async def get_current_tenant_context(request: Request) -> str:
    """
    Get current tenant context (alias for compatibility)

    Args:
        request: FastAPI request object

    Returns:
        str: Current tenant ID
    """
    return await get_tenant_context(request)
