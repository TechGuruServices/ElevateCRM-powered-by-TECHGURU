"""
TECHGURU ElevateCRM Authentication Configuration

Handles OIDC authentication with Keycloak integration.
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import jwt
from jwt import PyJWK, PyJWKClient
import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import settings


class AuthConfig:
    """Authentication configuration"""
    
    def __init__(self):
        # Keycloak configuration
        self.keycloak_server_url = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
        self.keycloak_realm = os.getenv("KEYCLOAK_REALM", "elevatecrm")
        self.keycloak_client_id = os.getenv("KEYCLOAK_CLIENT_ID", "elevatecrm-api")
        self.keycloak_client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
        
        # JWT configuration
        self.jwt_algorithm = "RS256"
        self.jwt_issuer = f"{self.keycloak_server_url}/realms/{self.keycloak_realm}"
        self.jwks_uri = f"{self.jwt_issuer}/protocol/openid-connect/certs"
        
        # Token validation
        self.verify_signature = os.getenv("JWT_VERIFY_SIGNATURE", "true").lower() == "true"
        self.verify_exp = os.getenv("JWT_VERIFY_EXP", "true").lower() == "true"
        self.verify_aud = os.getenv("JWT_VERIFY_AUD", "false").lower() == "true"
        
        # JWK Client for token verification
        self.jwks_client = PyJWKClient(self.jwks_uri) if self.verify_signature else None


class UserProfile(BaseModel):
    """User profile from JWT token"""
    sub: str  # Subject (user ID)
    email: Optional[str] = None
    email_verified: Optional[bool] = False
    preferred_username: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = []
    groups: list[str] = []
    company_id: Optional[str] = None
    
    # Token metadata
    iss: str  # Issuer
    aud: Optional[str] = None  # Audience
    iat: int  # Issued at
    exp: int  # Expiration
    auth_time: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now(timezone.utc).timestamp() > self.exp
    
    @property
    def display_name(self) -> str:
        """Get user display name"""
        return self.name or self.preferred_username or self.email or f"User {self.sub}"
    
    @property
    def full_name(self) -> str:
        """Get user full name"""
        if self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        return self.name or self.display_name


# Global auth config instance
auth_config = AuthConfig()


async def validate_jwt_token(token: str) -> UserProfile:
    """
    Validate JWT token and extract user profile
    
    Args:
        token: JWT token string
        
    Returns:
        UserProfile: Validated user profile
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode token header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        
        # Get signing key
        signing_key = None
        if auth_config.verify_signature and auth_config.jwks_client:
            try:
                signing_key = auth_config.jwks_client.get_signing_key_from_jwt(token)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to get signing key: {str(e)}"
                )
        
        # Decode and validate token
        decode_options = {
            "verify_signature": auth_config.verify_signature,
            "verify_exp": auth_config.verify_exp,
            "verify_aud": auth_config.verify_aud
        }
        
        if signing_key:
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[auth_config.jwt_algorithm],
                issuer=auth_config.jwt_issuer,
                options=decode_options
            )
        else:
            # For development - decode without verification
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False, "verify_aud": False}
            )
        
        # Extract roles from token
        roles = []
        
        # Keycloak realm roles
        if "realm_access" in payload and "roles" in payload["realm_access"]:
            roles.extend(payload["realm_access"]["roles"])
        
        # Keycloak client roles
        if "resource_access" in payload:
            client_access = payload["resource_access"].get(auth_config.keycloak_client_id, {})
            if "roles" in client_access:
                roles.extend(client_access["roles"])
        
        # Extract groups
        groups = payload.get("groups", [])
        
        # Extract company_id from custom claims or groups
        company_id = None
        if "company_id" in payload:
            company_id = payload["company_id"]
        elif groups:
            # Try to extract company ID from group names
            for group in groups:
                if group.startswith("company-"):
                    company_id = group.replace("company-", "")
                    break
        
        # Create user profile
        profile = UserProfile(
            sub=payload["sub"],
            email=payload.get("email"),
            email_verified=payload.get("email_verified", False),
            preferred_username=payload.get("preferred_username"),
            given_name=payload.get("given_name"),
            family_name=payload.get("family_name"),
            name=payload.get("name"),
            roles=roles,
            groups=groups,
            company_id=company_id,
            iss=payload["iss"],
            aud=payload.get("aud"),
            iat=payload["iat"],
            exp=payload["exp"],
            auth_time=payload.get("auth_time")
        )
        
        return profile
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


async def get_keycloak_user_info(access_token: str) -> Dict[str, Any]:
    """
    Get user info from Keycloak userinfo endpoint
    
    Args:
        access_token: Valid access token
        
    Returns:
        Dict containing user information
    """
    userinfo_url = f"{auth_config.jwt_issuer}/protocol/openid-connect/userinfo"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(userinfo_url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info from Keycloak"
            )
        
        return response.json()


def extract_bearer_token(authorization: str) -> str:
    """
    Extract bearer token from Authorization header
    
    Args:
        authorization: Authorization header value
        
    Returns:
        str: Bearer token
        
    Raises:
        HTTPException: If header is malformed
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    return parts[1]


def check_user_permissions(user: UserProfile, required_roles: list[str] = None, 
                         required_permissions: list[str] = None) -> bool:
    """
    Check if user has required roles or permissions
    
    Args:
        user: User profile
        required_roles: List of required roles
        required_permissions: List of required permissions
        
    Returns:
        bool: True if user has required access
    """
    # Super admin bypass
    if "admin" in user.roles or "super-admin" in user.roles:
        return True
    
    # Check roles
    if required_roles:
        if not any(role in user.roles for role in required_roles):
            return False
    
    # Check permissions (for future implementation)
    if required_permissions:
        # This would be implemented when we add permissions to user profiles
        # For now, assume admin role has all permissions
        if not ("admin" in user.roles or "manager" in user.roles):
            return False
    
    return True
