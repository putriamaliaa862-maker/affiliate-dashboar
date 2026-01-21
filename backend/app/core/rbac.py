"""
RBAC Helper for Shopee Account Scoping
Determines which accounts a user can access based on their role
"""
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.models.shopee_account import ShopeeAccount
from app.models.shopee_account_assignment import ShopeeAccountAssignment


def get_allowed_account_ids(db: Session, user: User) -> List[int]:
    """
    Get list of shopee_account IDs that user can access based on role.
    
    Rules:
    - super_admin, owner, supervisor: ALL accounts
    - leader, partner: Only assigned accounts
    - host: Only assigned accounts (read-only, enforce elsewhere)
    - Others: No accounts
    
    Returns:
        List[int]: Account IDs user can access
    """
    # Full access roles
    if user.role in ['super_admin', 'owner', 'supervisor']:
        accounts = db.query(ShopeeAccount.id).all()
        return [acc[0] for acc in accounts]
    
    # Scoped roles (leader, partner, host)
    if user.role in ['leader', 'partner', 'host']:
        assignments = db.query(ShopeeAccountAssignment.shopee_account_id).filter(
            ShopeeAccountAssignment.user_id == user.id
        ).all()
        return [assn[0] for assn in assignments]
    
    # Default: no access
    return []


def can_access_account(db: Session, user: User, account_id: int) -> bool:
    """
    Check if user can access specific account.
    
    Args:
        db: Database session
        user: Current user
        account_id: Shopee account ID to check
    
    Returns:
        bool: True if user has access
    """
    allowed_ids = get_allowed_account_ids(db, user)
    return account_id in allowed_ids


def is_read_only_for_account(user: User) -> bool:
    """
    Check if user has read-only access (e.g., 'host' role).
    
    Args:
        user: Current user
    
    Returns:
        bool: True if read-only
    """
    return user.role == 'host'
