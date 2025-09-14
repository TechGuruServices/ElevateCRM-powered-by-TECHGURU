"""
TECHGURU ElevateCRM Users Endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.dependencies import get_current_user, require_admin, get_current_user_from_db
from app.core.auth import UserProfile
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_users(
    current_user: UserProfile = Depends(require_admin)
) -> Dict[str, Any]:
    """List users for current tenant (admin only)"""
    return {
        "users": [],
        "total": 0,
        "limit": 10,
        "offset": 0,
        "tenant_id": current_user.company_id
    }


@router.get("/me")
async def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current authenticated user profile"""
    return {
        "id": current_user.sub,
        "email": current_user.email,
        "name": current_user.display_name,
        "full_name": current_user.full_name,
        "company_id": current_user.company_id,
        "roles": current_user.roles,
        "groups": current_user.groups,
        "email_verified": current_user.email_verified
    }


@router.get("/me/db")
async def get_current_user_from_database(
    user: User = Depends(get_current_user_from_db)
) -> Dict[str, Any]:
    """Get current user from database"""
    return {
        "id": str(user.id),
        "company_id": str(user.company_id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": user.display_name,
        "roles": user.roles,
        "permissions": user.permissions,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
    }
