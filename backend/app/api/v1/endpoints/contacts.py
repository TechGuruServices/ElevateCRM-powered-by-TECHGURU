"""
TECHGURU ElevateCRM Contacts Endpoints
"""
from fastapi import APIRouter, Query, Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Dict, Any, Optional, List
import logging

from app.core.dependencies import get_tenant_db, get_current_tenant
from app.models.contact import Contact

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_contacts(
    request: Request,
    response: Response,
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of contacts to return"),
    offset: int = Query(0, ge=0, description="Number of contacts to skip"),
    db: AsyncSession = Depends(get_tenant_db)
) -> Dict[str, Any]:
    """
    List contacts for current tenant with search, pagination, and filtering.
    
    - **q**: Search query (searches name, email, phone, company)
    - **limit**: Maximum number of contacts to return (1-100)
    - **offset**: Number of contacts to skip for pagination
    
    Returns contacts with X-Total-Count header for frontend pagination.
    """
    try:
        # Build base query - RLS automatically filters by tenant
        query = select(Contact)
        count_query = select(func.count(Contact.id))
        
        # Apply search filter if provided
        if q:
            search_filter = or_(
                Contact.first_name.ilike(f"%{q}%"),
                Contact.last_name.ilike(f"%{q}%"),
                Contact.email.ilike(f"%{q}%"),
                Contact.phone.ilike(f"%{q}%"),
                Contact.company.ilike(f"%{q}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count for X-Total-Count header
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Contact.first_name, Contact.last_name)
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        contacts = result.scalars().all()
        
        # Set X-Total-Count header for frontend pagination
        response.headers["X-Total-Count"] = str(total_count)
        
        # Convert to response format
        contacts_data = []
        for contact in contacts:
            contacts_data.append({
                "id": str(contact.id),
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "title": contact.title,
                "status": contact.status,
                "tags": contact.tags,
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
            })
        
        logger.info(f"Retrieved {len(contacts_data)} contacts (total: {total_count})")
        
        return {
            "contacts": contacts_data,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "query": q,
            "has_more": offset + len(contacts_data) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contacts"
        )


@router.get("/{contact_id}")
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_tenant_db)
) -> Dict[str, Any]:
    """
    Get a specific contact by ID.
    
    Returns contact details if found and accessible by current tenant.
    """
    try:
        # Query contact by ID - RLS automatically filters by tenant
        query = select(Contact).where(Contact.id == contact_id)
        result = await db.execute(query)
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        return {
            "id": str(contact.id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "company": contact.company,
            "title": contact.title,
            "status": contact.status,
            "tags": contact.tags,
            "notes": contact.notes,
            "address": {
                "line1": contact.address_line1,
                "line2": contact.address_line2,
                "city": contact.city,
                "state": contact.state,
                "postal_code": contact.postal_code,
                "country": contact.country
            },
            "social": {
                "linkedin": contact.linkedin_url,
                "twitter": contact.twitter_handle,
                "website": contact.website
            },
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
            "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving contact {contact_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact"
        )
