"""
Authentication dependencies for FastAPI route protection.
Implements role-based access control (RBAC).
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.auth.jwt import verify_token

# HTTP Bearer security scheme
security = HTTPBearer()

# Role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    "super_admin": 4,
    "admin": 3,
    "leader": 2,
    "affiliate": 1
}




def normalize_role(role: str) -> str:
    """
    Normalize role string to standard format (lowercase, snake_case).
    Example: "Super Admin" -> "super_admin"
    """
    if not role:
        return ""
    return role.strip().lower().replace(" ", "_").replace("-", "_")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Convert string sub to integer for database query
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Normalize role on the fly
    user.role = normalize_role(user.role)
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active (redundant check)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(minimum_role: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin")
        async def admin_only(user: User = Depends(require_role("admin"))):
            ...
    
    Args:
        minimum_role: Minimum required role (super_admin, admin, leader, affiliate)
    
    Returns:
        Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_level = ROLE_HIERARCHY.get(minimum_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum_role} role or higher. Your role: {current_user.role}"
            )
        
        return current_user
    
    return role_checker


def check_resource_access(user: User, resource_owner_id: int) -> bool:
    """
    Check if user can access a resource.
    
    Rules:
    - super_admin, admin: Access all resources
    - leader: Access own resources + team members' resources
    - affiliate: Access only own resources
    
    Args:
        user: Current authenticated user
        resource_owner_id: ID of the user who owns the resource
    
    Returns:
        True if access allowed, False otherwise
    """
    # Admins can access everything
    if user.role in ['super_admin', 'admin']:
        return True
    
    # Can access own resources
    if user.id == resource_owner_id:
        return True
    
    # Leaders can access team members' resources
    if user.role == 'leader':
        # Check if resource_owner is in leader's team
        # This would require a DB query in actual implementation
        return False  # Simplified for now
    
    return False


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise None.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
        
    except Exception:
        return None
