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

router = APIRouter()


@router.get("/")
def list_accounts(
    request: Request,
    studio_id: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all Shopee accounts or by studio.
    RBAC: Owner/Admin (All), Host (Scoped)
    """
    start_time = time.time()
    logger.info(f"Accounts List: User={current_user.username} Role={current_user.role}")

    # RBAC Check (Access Control)
    # Re-using financial access permission as a general 'can view business data' check
    # Or strict check just for this module
    if current_user.role not in ["super_admin", "admin", "owner", "supervisor", "partner", "leader", "host", "affiliate"]:
         raise HTTPException(status_code=403, detail="Forbidden")

    query = db.query(ShopeeAccount)
    
    # Optional: Apply Scope if needed (e.g. Host only sees their accounts?)
    # Currently ShopeeAccount doesn't have handler_id directly, but we might want to restrict later.
    # For now, allow all accounts viewable by authorized users, OR apply scope if logic available.
    
    if studio_id:
        query = query.filter(ShopeeAccount.studio_id == studio_id)
        
    accounts = query.all()
    
    duration = (time.time() - start_time) * 1000
    logger.info(f"Accounts Fetched: {len(accounts)} records in {duration:.2f}ms")
    
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
