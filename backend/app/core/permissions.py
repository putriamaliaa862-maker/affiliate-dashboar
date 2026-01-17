import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount

# Setup logger
logger = logging.getLogger(__name__)

# Roles allowed to access full data
FULL_ACCESS_ROLES = ["super_admin", "admin", "owner", "supervisor", "partner", "leader"]
# Roles allowed with restrictions
RESTRICTED_ROLES = ["host", "affiliate"]

def verify_financial_access(user: User, endpoint_name: str) -> bool:
    """
    Verify if user has permission to access financial/analytics data.
    Logs access attempt.
    """
    # 1. Logging Access
    logger.info(f"Access Check: User={user.username} Role={user.role} Endpoint={endpoint_name}")

    if user.role in FULL_ACCESS_ROLES:
        return True
    
    if user.role in RESTRICTED_ROLES:
        return True
        
    logger.warning(f"Access Blocked: Role {user.role} not allowed for {endpoint_name}")
    return False

def apply_scope_restriction(query, user: User, model=Order):
    """
    Apply filter to query based on user role.
    - Full Access Roles: No filter
    - Restricted Roles (Host/Affiliate): Filter by handler_user_id
    """
    if user.role in FULL_ACCESS_ROLES:
        return query
        
    if user.role in RESTRICTED_ROLES:
        # Host/Affiliate sees only orders they handle
        if hasattr(model, 'handler_user_id'):
            return query.filter(model.handler_user_id == user.id)
        else:
            # Fallback if model doesn't have handler_user_id (e.g. accessing Account directly)
            # This logic depends on the model passed.
            # If model is ShopeeAccount, maybe we need a join or logic.
            # For now, strict block if no handler_key found
            logger.warning(f"Scope restriction applied but model {model} has no handler_user_id")
            return query.filter(model.id == -1) # Return empty
            
    return query

def get_allowed_account_ids(db: Session, user: User) -> list[int]:
    """
    Get list of account IDs that the user is allowed to access.
    
    Rules:
    - Super Admin / Owner / Supervisor / Partner: All accounts
    - Leader: Assigned accounts (For now: All accounts in their studio/system if no explicit assignment found)
    - Host: Assigned accounts (For now: All accounts, View Only enforced by endpoint logic)
    
    TODO: Implement explicit User-Account assignment table if strictly required.
    For this Sprint 2, we assume Leaders/Hosts operate within their Studio context (if any) or see all.
    Given the constraint 'Jangan merusak modul existing', we cannot add a new relation table easily.
    We will fallback to returning all active account IDs for everyone, 
    BUT Routes will enforce Action permissions (Host cannot POST).
    """
    if user.role in FULL_ACCESS_ROLES or user.role in ["leader", "host"]:
        # Return all active account IDs
        accounts = db.query(ShopeeAccount.id).filter(ShopeeAccount.is_active == True).all()
        return [a.id for a in accounts]
    
    # Default: No access
    return []
