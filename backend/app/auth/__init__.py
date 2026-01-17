"""Auth module initialization"""
from app.auth.jwt import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_role,
    check_resource_access,
    ROLE_HIERARCHY
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "check_resource_access",
    "ROLE_HIERARCHY"
]
