"""
TECHGURU ElevateCRM Authentication API Endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.auth import auth_config, get_keycloak_user_info, UserProfile
from app.core.dependencies import get_current_user, get_current_user_optional

router = APIRouter()


class AuthInfo(BaseModel):
    """Authentication information response"""
    keycloak_server_url: str
    keycloak_realm: str
    client_id: str
    issuer: str
    auth_url: str
    logout_url: str


class UserInfo(BaseModel):
    """User information response"""
    sub: str
    email: str
    email_verified: bool
    preferred_username: str
    given_name: str
    family_name: str
    name: str
    display_name: str
    full_name: str
    roles: list[str]
    groups: list[str]
    company_id: str | None


@router.get("/auth/info", response_model=AuthInfo)
async def get_auth_info():
    """
    Get authentication configuration information
    
    Returns information needed for frontend authentication setup
    """
    return AuthInfo(
        keycloak_server_url=auth_config.keycloak_server_url,
        keycloak_realm=auth_config.keycloak_realm,
        client_id=auth_config.keycloak_client_id,
        issuer=auth_config.jwt_issuer,
        auth_url=f"{auth_config.jwt_issuer}/protocol/openid-connect/auth",
        logout_url=f"{auth_config.jwt_issuer}/protocol/openid-connect/logout"
    )


@router.get("/auth/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserInfo: Current user information
    """
    return UserInfo(
        sub=current_user.sub,
        email=current_user.email or "",
        email_verified=current_user.email_verified,
        preferred_username=current_user.preferred_username or "",
        given_name=current_user.given_name or "",
        family_name=current_user.family_name or "",
        name=current_user.name or "",
        display_name=current_user.display_name,
        full_name=current_user.full_name,
        roles=current_user.roles,
        groups=current_user.groups,
        company_id=current_user.company_id
    )


@router.get("/auth/userinfo")
async def get_userinfo_from_keycloak(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user info directly from Keycloak userinfo endpoint
    
    This is useful for getting the most up-to-date user information
    """
    try:
        # Note: This would need the original access token, which we don't store
        # For now, return the token-derived information
        return {
            "sub": current_user.sub,
            "email": current_user.email,
            "email_verified": current_user.email_verified,
            "preferred_username": current_user.preferred_username,
            "given_name": current_user.given_name,
            "family_name": current_user.family_name,
            "name": current_user.name,
            "roles": current_user.roles,
            "groups": current_user.groups,
            "company_id": current_user.company_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )


@router.post("/auth/validate")
async def validate_token(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Validate the provided JWT token
    
    Args:
        current_user: Current authenticated user (validates token)
        
    Returns:
        Validation status and user info
    """
    return {
        "valid": True,
        "user": {
            "sub": current_user.sub,
            "email": current_user.email,
            "roles": current_user.roles,
            "company_id": current_user.company_id,
            "expires_at": current_user.exp
        }
    }


@router.get("/auth/status")
async def get_auth_status(
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Get authentication status (works with or without token)
    
    Args:
        current_user: Optional current user
        
    Returns:
        Authentication status
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "sub": current_user.sub,
                "email": current_user.email,
                "display_name": current_user.display_name,
                "roles": current_user.roles,
                "company_id": current_user.company_id
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }


@router.get("/auth/health")
async def auth_health_check():
    """
    Health check for authentication service
    
    Returns:
        Authentication service status
    """
    try:
        # Test Keycloak connectivity by checking the JWKS endpoint
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(auth_config.jwks_uri, timeout=5.0)
            keycloak_accessible = response.status_code == 200
        
        return {
            "status": "healthy" if keycloak_accessible else "degraded",
            "keycloak_accessible": keycloak_accessible,
            "keycloak_server": auth_config.keycloak_server_url,
            "realm": auth_config.keycloak_realm,
            "jwks_uri": auth_config.jwks_uri
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "keycloak_accessible": False,
            "error": str(e),
            "keycloak_server": auth_config.keycloak_server_url,
            "realm": auth_config.keycloak_realm
        }
