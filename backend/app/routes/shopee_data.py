from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order  # Use Order instead of Transaction
from pydantic import BaseModel

router = APIRouter()


# ========== SCHEMAS ==========

class ShopeeProductData(BaseModel):
    product_id: str
    product_name: str
    price: float
    sold_qty: int = 0
    gmv: float = 0.0
    commission: float = 0.0
    clicks: Optional[int] = None


class ShopeeSyncRequest(BaseModel):
    account_id: Optional[int] = None
    shop_name: Optional[str] = None
    account_name: Optional[str] = None
    sync_date: Optional[str] = None  # YYYY-MM-DD
    source: str = "extension"  # extension, manual, live
    products: List[ShopeeProductData] = []
    raw_data: Optional[dict] = None


class SyncStatusResponse(BaseModel):
    success: bool
    message: str
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    synced_products: int = 0
    timestamp: str


# ========== ENDPOINTS ==========

@router.post("/sync", response_model=SyncStatusResponse)
async def sync_shopee_data(
    payload: ShopeeSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync Shopee data from extension/manual input
    Persists to orders table and creates sync log
    """
    try:
        # 1. Find or create Shopee Account
        account = None
        account_name_final = None
        
        if payload.account_id:
            account = db.query(ShopeeAccount).filter(ShopeeAccount.id == payload.account_id).first()
            if account:
                account_name_final = account.account_name
        
        # Fallback: try to find by shop_name or account_name
        if not account:
            search_name = payload.shop_name or payload.account_name
            if search_name:
                account = db.query(ShopeeAccount).filter(
                    ShopeeAccount.account_name.ilike(f"%{search_name}%")
                ).first()
                if account:
                    account_name_final = account.account_name
        
        # If still not found, use fallback name
        if not account_name_final:
            account_name_final = payload.shop_name or payload.account_name or f"Auto-imported: {payload.account_id or 'Unknown'}"
        
        # 2. Parse sync date
        sync_date = date.today()
        if payload.sync_date:
            try:
                sync_date = datetime.strptime(payload.sync_date, "%Y-%m-%d").date()
            except:
                pass
        
        # 3. Persist products as orders
        synced_count = 0
        for product in payload.products:
            # Create order for each product sync
            # Using product_id as order_id (might want to generate unique IDs instead)
            order_id = f"SYNC-{product.product_id}-{sync_date.strftime('%Y%m%d')}"
            
            existing = db.query(Order).filter(
                Order.order_id == order_id
            ).first()
            
            if existing:
                # Update existing order
                existing.total_amount = product.gmv
                existing.commission_amount = product.commission
                existing.product_name = product.product_name
                existing.product_id = product.product_id
                existing.updated_at = datetime.utcnow()
            else:
                # Create new order
                order = Order(
                    shopee_account_id=account.id if account else None,
                    order_id=order_id,
                    total_amount=product.gmv,
                    commission_amount=product.commission,
                    status="completed",
                    date=datetime.combine(sync_date, datetime.min.time()),
                    product_name=product.product_name,
                    product_id=product.product_id,
                    handler_user_id=current_user.id,
                    created_at=datetime.utcnow()
                )
                db.add(order)
            
            synced_count += 1
        
        db.commit()
        
        return SyncStatusResponse(
            success=True,
            message=f"Successfully synced {synced_count} products",
            account_id=account.id if account else None,
            account_name=account_name_final,
            synced_products=synced_count,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/status")
async def get_sync_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sync status and latest sync info
    """
    # Get latest orders
    latest_sync = db.query(Order).order_by(Order.created_at.desc()).first()
    
    if not latest_sync:
        return {
            "status": "no_sync",
            "message": "No sync data available",
            "last_sync_at": None
        }
    
    return {
        "status": "ok",
        "message": "Sync data available",
        "last_sync_at": latest_sync.created_at.isoformat(),
        "total_orders": db.query(Order).count()
    }

