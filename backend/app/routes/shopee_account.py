import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shopee_account import ShopeeAccount
from app.models.studio import Studio
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.core.permissions import verify_financial_access, apply_scope_restriction

# Setup Logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shopee-accounts", tags=["Shopee Accounts"])


@router.get("/")
def list_accounts(
    request: Request,
    studio_id: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all Shopee accounts with RBAC scoping.
    
    RBAC Rules:
    - super_admin/owner/supervisor: ALL accounts
    - leader/partner: Only assigned accounts
    - host: Only assigned accounts (read-only)
    """
    start_time = time.time()
    logger.info(f"Accounts List: User={current_user.username} Role={current_user.role}")

    # RBAC Check - import here to avoid circular dependency
    from app.core.rbac import get_allowed_account_ids
    
    # Get allowed account IDs for this user
    allowed_account_ids = get_allowed_account_ids(db, current_user)
    
    logger.info(f"RBAC: User {current_user.id} can access {len(allowed_account_ids)} accounts")
    
    # Build query with RBAC filtering
    query = db.query(ShopeeAccount)
    
    # Apply RBAC scope (unless user has full access)
    if current_user.role not in ['super_admin', 'owner', 'supervisor']:
        if not allowed_account_ids:
            # User has no assigned accounts
            logger.warning(f"User {current_user.id} has no assigned accounts")
            return []
        query = query.filter(ShopeeAccount.id.in_(allowed_account_ids))
    
    # Apply optional studio filter
    if studio_id:
        query = query.filter(ShopeeAccount.studio_id == studio_id)
        
    accounts = query.all()
    
    duration = (time.time() - start_time) * 1000
    logger.info(f"Accounts Fetched: {len(accounts)} records in {duration:.2f}ms")
    
    return accounts


@router.get("/my")
def get_my_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get accounts assigned to current user only.
    Always returns scoped view regardless of role.
    """
    from app.core.rbac import get_allowed_account_ids
    
    allowed_account_ids = get_allowed_account_ids(db, current_user)
    
    if not allowed_account_ids:
        logger.info(f"User {current_user.id} has no assigned accounts")
        return []
    
    accounts = db.query(ShopeeAccount).filter(
        ShopeeAccount.id.in_(allowed_account_ids)
    ).all()
    
    logger.info(f"User {current_user.id} retrieved {len(accounts)} assigned accounts")
    return accounts


@router.post("/")
def create_account(
    account: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new Shopee account"""
    # Only Admin/Owner/Supervisor
    if current_user.role not in ["super_admin", "admin", "owner", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized to create accounts")

    # Validate studio exists
    studio = db.query(Studio).filter(Studio.id == account["studio_id"]).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    
    db_account = ShopeeAccount(
        studio_id=account["studio_id"],
        account_name=account["account_name"],
        shopee_account_id=account.get("shopee_account_id"),
        refresh_token=account.get("refresh_token"),
        access_token=account.get("access_token"),
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return {"id": db_account.id, "account_name": db_account.account_name}


@router.get("/{account_id}")
def get_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get account by ID"""
    account = db.query(ShopeeAccount).filter(ShopeeAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "id": account.id,
        "account_name": account.account_name,
        "studio_id": account.studio_id,
        "is_active": account.is_active,
    }


@router.put("/{account_id}")
def update_account(
    account_id: int, 
    account: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update Shopee account"""
    # Only Admin/Owner/Supervisor
    if current_user.role not in ["super_admin", "admin", "owner", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized to update accounts")

    db_account = db.query(ShopeeAccount).filter(ShopeeAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in account.items():
        if hasattr(db_account, key) and key not in ["id", "created_at"]:
            setattr(db_account, key, value)
    
    db.commit()
    return {"message": "Account updated"}


@router.delete("/{account_id}")
def delete_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete account"""
    # Only Admin/Owner
    if current_user.role not in ["super_admin", "admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete accounts")

    db_account = db.query(ShopeeAccount).filter(ShopeeAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(db_account)
    db.commit()
    return {"message": "Account deleted"}
