"""
TECHGURU ElevateCRM Tenant Context Management

SQLite-compatible tenant isolation through application-level filtering.
Since SQLite doesn't support PostgreSQL's Row Level Security (RLS), 
we implement tenant isolation at the application layer.
"""
import logging
from contextvars import ContextVar
from typing import Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy import Column

logger = logging.getLogger(__name__)

# Context variable to store current tenant ID across async boundaries
current_tenant_id: ContextVar[Optional[str]] = ContextVar('current_tenant_id', default=None)


class TenantContextManager:
    """Manages tenant context for multi-tenant data isolation"""
    
    @staticmethod
    def set_tenant_id(tenant_id: str) -> None:
        """Set the current tenant ID in the context"""
        if not tenant_id:
            raise ValueError("Tenant ID cannot be empty")
        
        current_tenant_id.set(tenant_id)
        logger.debug(f"Set tenant context: {tenant_id}")
    
    @staticmethod
    def get_tenant_id() -> Optional[str]:
        """Get the current tenant ID from context"""
        return current_tenant_id.get()
    
    @staticmethod
    def clear_tenant_id() -> None:
        """Clear the current tenant ID from context"""
        current_tenant_id.set(None)
        logger.debug("Cleared tenant context")
    
    @staticmethod
    def require_tenant_id() -> str:
        """Get the current tenant ID, raising an error if not set"""
        tenant_id = current_tenant_id.get()
        if not tenant_id:
            raise ValueError("No tenant context set. Tenant ID is required for this operation.")
        return tenant_id


class TenantQueryFilter:
    """Automatic tenant filtering for SQLAlchemy queries"""
    
    @staticmethod
    def apply_tenant_filter(query: Select, model: Any) -> Select:
        """
        Apply tenant filtering to a SQLAlchemy query
        
        Args:
            query: The SQLAlchemy Select query
            model: The SQLAlchemy model class
            
        Returns:
            Modified query with tenant filter applied
        """
        import uuid
        
        tenant_id = TenantContextManager.get_tenant_id()
        if not tenant_id:
            logger.warning("No tenant context set - query will return no results for safety")
            # Return a query that will return no results for safety
            return query.where(False)
        
        # Check if model has company_id field (tenant-scoped)
        if hasattr(model, 'company_id'):
            logger.debug(f"Applying tenant filter for {model.__name__}: {tenant_id}")
            # Convert string UUID to UUID object for comparison
            if isinstance(tenant_id, str):
                try:
                    tenant_uuid = uuid.UUID(tenant_id)
                    return query.where(model.company_id == tenant_uuid)
                except ValueError:
                    # Fallback to string comparison
                    return query.where(model.company_id == tenant_id)
            else:
                return query.where(model.company_id == tenant_id)
        
        # Special case for Company model - filter by id instead of company_id
        elif hasattr(model, 'id') and model.__name__ == 'Company':
            logger.debug(f"Applying company filter for {model.__name__}: {tenant_id}")
            # Convert string UUID to UUID object for comparison
            if isinstance(tenant_id, str):
                try:
                    tenant_uuid = uuid.UUID(tenant_id)
                    return query.where(model.id == tenant_uuid)
                except ValueError:
                    # Fallback to string comparison
                    return query.where(model.id == tenant_id)
            else:
                return query.where(model.id == tenant_id)
        
        else:
            logger.debug(f"No tenant filtering applied for {model.__name__} - not tenant-scoped")
            return query
    
    @staticmethod
    def validate_tenant_access(instance: Any, tenant_id: Optional[str] = None) -> bool:
        """
        Validate that an instance belongs to the current tenant
        
        Args:
            instance: The model instance to validate
            tenant_id: Optional tenant ID to check against (uses context if not provided)
            
        Returns:
            True if instance belongs to tenant, False otherwise
        """
        if tenant_id is None:
            tenant_id = TenantContextManager.get_tenant_id()
        
        if not tenant_id:
            logger.warning("No tenant context set - denying access")
            return False
        
        # Check company_id for tenant-scoped models
        if hasattr(instance, 'company_id'):
            return str(instance.company_id) == tenant_id
        
        # Special case for Company model
        elif hasattr(instance, 'id') and instance.__class__.__name__ == 'Company':
            return str(instance.id) == tenant_id
        
        # Non-tenant-scoped models are always accessible
        else:
            return True


def ensure_tenant_isolation(func):
    """
    Decorator to ensure tenant isolation for database operations
    
    Usage:
        @ensure_tenant_isolation
        async def get_contacts(db: Session):
            # This will automatically filter by tenant
            return await db.execute(select(Contact))
    """
    def wrapper(*args, **kwargs):
        tenant_id = TenantContextManager.get_tenant_id()
        if not tenant_id:
            raise ValueError("No tenant context set. Cannot perform tenant-scoped operations.")
        
        logger.debug(f"Ensuring tenant isolation for {func.__name__}: {tenant_id}")
        return func(*args, **kwargs)
    
    return wrapper


# Helper functions for common operations
def get_current_tenant_id() -> str:
    """Get current tenant ID, raising error if not set"""
    return TenantContextManager.require_tenant_id()


def is_tenant_scoped_model(model: Any) -> bool:
    """Check if a model is tenant-scoped (has company_id)"""
    return hasattr(model, 'company_id') or (
        hasattr(model, 'id') and model.__name__ == 'Company'
    )


def create_tenant_scoped_instance(model_class: Any, **kwargs) -> Any:
    """
    Create a new instance with automatic tenant ID assignment
    
    Args:
        model_class: The SQLAlchemy model class
        **kwargs: Other fields for the instance
        
    Returns:
        New model instance with tenant ID set
    """
    import uuid
    
    tenant_id = TenantContextManager.require_tenant_id()
    
    # Set company_id for tenant-scoped models
    if hasattr(model_class, 'company_id') and 'company_id' not in kwargs:
        # Convert string UUID to UUID object if needed
        if isinstance(tenant_id, str):
            try:
                kwargs['company_id'] = uuid.UUID(tenant_id)
            except ValueError:
                kwargs['company_id'] = tenant_id  # fallback to string
        else:
            kwargs['company_id'] = tenant_id
    
    logger.debug(f"Creating tenant-scoped {model_class.__name__} for tenant: {tenant_id}")
    return model_class(**kwargs)


# Alias for backward compatibility with existing imports
TenantContext = TenantContextManager
