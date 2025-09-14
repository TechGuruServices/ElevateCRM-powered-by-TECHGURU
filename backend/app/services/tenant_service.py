"""
TECHGURU ElevateCRM Tenant-Aware Database Service

SQLite-compatible service layer that automatically applies tenant filtering
to database queries, replacing PostgreSQL Row Level Security (RLS).
"""
import logging
from typing import Type, TypeVar, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.sql import Select, Update, Delete

from app.core.tenant_context import TenantContextManager, TenantQueryFilter, create_tenant_scoped_instance

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class TenantAwareService:
    """Base service class with automatic tenant filtering for all operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # READ Operations with automatic tenant filtering
    
    async def get_by_id(
        self, 
        model: Type[ModelType], 
        id: Any, 
        validate_tenant: bool = True
    ) -> Optional[ModelType]:
        """
        Get a single record by ID with tenant filtering
        
        Args:
            model: SQLAlchemy model class
            id: Primary key value
            validate_tenant: Whether to validate tenant access (default: True)
            
        Returns:
            Model instance or None if not found or access denied
        """
        query = select(model).where(model.id == id)
        
        if validate_tenant:
            query = TenantQueryFilter.apply_tenant_filter(query, model)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        model: Type[ModelType],
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """
        Get all records with tenant filtering and optional additional filters
        
        Args:
            model: SQLAlchemy model class
            filters: Optional dictionary of field filters
            order_by: Optional field name to order by
            limit: Optional limit for pagination
            offset: Optional offset for pagination
            
        Returns:
            List of model instances
        """
        query = select(model)
        
        # Apply tenant filtering
        query = TenantQueryFilter.apply_tenant_filter(query, model)
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
        
        # Apply ordering
        if order_by and hasattr(model, order_by):
            query = query.order_by(getattr(model, order_by))
        
        # Apply pagination
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search(
        self,
        model: Type[ModelType],
        search_fields: List[str],
        search_term: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 50
    ) -> List[ModelType]:
        """
        Search records with tenant filtering
        
        Args:
            model: SQLAlchemy model class
            search_fields: List of field names to search in
            search_term: Search term
            filters: Optional additional filters
            limit: Maximum number of results
            
        Returns:
            List of matching model instances
        """
        query = select(model)
        
        # Apply tenant filtering
        query = TenantQueryFilter.apply_tenant_filter(query, model)
        
        # Apply search conditions
        if search_term and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(model, field):
                    field_attr = getattr(model, field)
                    search_conditions.append(
                        field_attr.ilike(f"%{search_term}%")
                    )
            
            if search_conditions:
                query = query.where(or_(*search_conditions))
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(
        self,
        model: Type[ModelType],
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records with tenant filtering
        
        Args:
            model: SQLAlchemy model class
            filters: Optional additional filters
            
        Returns:
            Count of matching records
        """
        query = select(func.count(model.id))
        
        # Apply tenant filtering
        query = TenantQueryFilter.apply_tenant_filter(query, model)
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    # WRITE Operations with automatic tenant assignment
    
    async def create(
        self,
        model: Type[ModelType],
        **data
    ) -> ModelType:
        """
        Create a new record with automatic tenant assignment
        
        Args:
            model: SQLAlchemy model class
            **data: Field data for the new record
            
        Returns:
            Created model instance
        """
        # Create instance with automatic tenant ID assignment
        instance = create_tenant_scoped_instance(model, **data)
        
        self.db.add(instance)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(instance)
        
        logger.debug(f"Created {model.__name__} with ID: {instance.id}")
        return instance
    
    async def update(
        self,
        model: Type[ModelType],
        id: Any,
        **data
    ) -> Optional[ModelType]:
        """
        Update a record with tenant validation
        
        Args:
            model: SQLAlchemy model class
            id: Primary key value
            **data: Field data to update
            
        Returns:
            Updated model instance or None if not found/access denied
        """
        # First get the record with tenant validation
        instance = await self.get_by_id(model, id, validate_tenant=True)
        if not instance:
            return None
        
        # Update fields
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        await self.db.flush()
        await self.db.refresh(instance)
        
        logger.debug(f"Updated {model.__name__} ID: {id}")
        return instance
    
    async def delete(
        self,
        model: Type[ModelType],
        id: Any
    ) -> bool:
        """
        Delete a record with tenant validation
        
        Args:
            model: SQLAlchemy model class
            id: Primary key value
            
        Returns:
            True if deleted, False if not found/access denied
        """
        # First get the record with tenant validation
        instance = await self.get_by_id(model, id, validate_tenant=True)
        if not instance:
            return False
        
        await self.db.delete(instance)
        await self.db.flush()
        
        logger.debug(f"Deleted {model.__name__} ID: {id}")
        return True
    
    async def bulk_update(
        self,
        model: Type[ModelType],
        filters: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> int:
        """
        Bulk update records with tenant filtering
        
        Args:
            model: SQLAlchemy model class
            filters: Conditions for records to update
            updates: Field updates to apply
            
        Returns:
            Number of updated records
        """
        query = update(model)
        
        # Apply tenant filtering
        tenant_id = TenantContextManager.get_tenant_id()
        if tenant_id and hasattr(model, 'company_id'):
            query = query.where(model.company_id == tenant_id)
        elif tenant_id and model.__name__ == 'Company':
            query = query.where(model.id == tenant_id)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(model, field):
                query = query.where(getattr(model, field) == value)
        
        # Apply updates
        query = query.values(**updates)
        
        result = await self.db.execute(query)
        await self.db.flush()
        
        updated_count = result.rowcount
        logger.debug(f"Bulk updated {updated_count} {model.__name__} records")
        return updated_count
    
    async def bulk_delete(
        self,
        model: Type[ModelType],
        filters: Dict[str, Any]
    ) -> int:
        """
        Bulk delete records with tenant filtering
        
        Args:
            model: SQLAlchemy model class
            filters: Conditions for records to delete
            
        Returns:
            Number of deleted records
        """
        query = delete(model)
        
        # Apply tenant filtering
        tenant_id = TenantContextManager.get_tenant_id()
        if tenant_id and hasattr(model, 'company_id'):
            query = query.where(model.company_id == tenant_id)
        elif tenant_id and model.__name__ == 'Company':
            query = query.where(model.id == tenant_id)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(model, field):
                query = query.where(getattr(model, field) == value)
        
        result = await self.db.execute(query)
        await self.db.flush()
        
        deleted_count = result.rowcount
        logger.debug(f"Bulk deleted {deleted_count} {model.__name__} records")
        return deleted_count


# Helper functions for creating tenant-aware services
def get_tenant_service(db: AsyncSession) -> TenantAwareService:
    """
    Create a tenant-aware service instance
    
    Args:
        db: Database session
        
    Returns:
        TenantAwareService instance
    """
    return TenantAwareService(db)


async def ensure_tenant_access(db: AsyncSession, model: Type[ModelType], id: Any) -> ModelType:
    """
    Get a record and ensure current tenant has access
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        id: Primary key value
        
    Returns:
        Model instance
        
    Raises:
        ValueError: If record not found or access denied
    """
    service = get_tenant_service(db)
    instance = await service.get_by_id(model, id, validate_tenant=True)
    
    if not instance:
        raise ValueError(f"{model.__name__} not found or access denied")
    
    return instance
