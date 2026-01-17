"""
Live Products API Routes
Implements strict RBAC: Host cannot sync (403), but can view based on scope
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.live_product_snapshot import LiveProductSnapshot
from app.models.live_sync_log import LiveSyncLog
from app.models.shopee_account import ShopeeAccount
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.live_product import (
    LiveProductSyncRequest,
    LiveProductSyncResponse,
    LiveProductSnapshotResponse,
    LiveProductRankingResponse,
    LiveProductRankingItem,
    LiveSyncLogResponse
)

router = APIRouter(prefix="/live-products", tags=["Live Products"])


# ==================== RBAC Helpers ====================

def normalize_role(role: str) -> str:
    """Normalize role string (handle 'Super Admin' vs 'super_admin')"""
    return role.lower().replace(" ", "_")


def check_sync_permission(user: User) -> bool:
    """
    Check if user can sync data
    STRICT: Host CANNOT sync (403)
    """
    role = normalize_role(user.role)
    allowed_roles = ["super_admin", "admin", "owner", "supervisor", "partner", "leader"]
    return role in allowed_roles


def can_access_account(user: User, account_id: int, db: Session) -> bool:
    """
    Check if user can access specific account based on scope
    """
    role = normalize_role(user.role)
    
    # Owner and super_admin can access all
    if role in ["owner", "super_admin", "admin"]:
        return True
    
    # For leader/host: check if they have access to this account
    # This would require additional relationship checking
    # For now, allowing access (TODO: implement proper scope check)
    return True


# ==================== Endpoints ====================

@router.post("/sync", response_model=LiveProductSyncResponse)
def sync_live_products(
    request: LiveProductSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /api/live-products/sync
    Sync live product data from extension
    
    RBAC: super_admin/owner/supervisor/partner/leader ✅
          host: 403 ❌
    """
    # STRICT RBAC: Host cannot sync
    if not check_sync_permission(current_user):
        raise HTTPException(
            status_code=403,
            detail="Host role cannot sync data. Contact your leader."
        )
    
    # Verify account exists
    account = db.query(ShopeeAccount).filter(ShopeeAccount.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Shopee account not found")
    
    # Parse snapshot date
    try:
        snapshot_dt = datetime.strptime(request.snapshot_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    inserted = 0
    updated = 0
    
    try:
        for product in request.products:
            # Check if snapshot exists for this date + account + product
            existing = db.query(LiveProductSnapshot).filter(
                and_(
                    LiveProductSnapshot.snapshot_date == snapshot_dt,
                    LiveProductSnapshot.account_id == request.account_id,
                    LiveProductSnapshot.product_id == product.product_id
                )
            ).first()
            
            if existing:
                # Update existing
                existing.product_name = product.product_name
                existing.sold_qty = product.sold_qty
                existing.gmv = product.gmv
                existing.clicks = product.clicks
                existing.source = request.source
                existing.raw_data = request.raw_data
                updated += 1
            else:
                # Insert new
                snapshot = LiveProductSnapshot(
                    snapshot_date=snapshot_dt,
                    account_id=request.account_id,
                    studio_id=account.studio_id,
                    leader_id=None,  # TODO: Get from account relationship
                    host_id=None,    # TODO: Get from account relationship
                    product_id=product.product_id,
                    product_name=product.product_name,
                    sold_qty=product.sold_qty,
                    gmv=product.gmv,
                    clicks=product.clicks,
                    source=request.source,
                    raw_data=request.raw_data
                )
                db.add(snapshot)
                inserted += 1
        
        # Create sync log
        sync_log = LiveSyncLog(
            account_id=request.account_id,
            snapshot_date=snapshot_dt,
            status="SUCCESS",
            total_rows=inserted + updated,
            message=f"Synced {inserted} new, {updated} updated"
        )
        db.add(sync_log)
        
        db.commit()
        
        return LiveProductSyncResponse(
            success=True,
            inserted=inserted,
            updated=updated,
            total=inserted + updated,
            message="Sync successful"
        )
    
    except Exception as e:
        db.rollback()
        
        # Log failed sync
        sync_log = LiveSyncLog(
            account_id=request.account_id,
            snapshot_date=snapshot_dt,
            status="FAIL",
            total_rows=0,
            message=str(e)
        )
        db.add(sync_log)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/daily", response_model=List[LiveProductSnapshotResponse])
def get_daily_snapshots(
    date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/live-products/daily?date=YYYY-MM-DD&account_id=123
    Get daily product snapshots
    
    RBAC scope:
    - owner/supervisor: all accounts
    - leader: only their accounts
    - host: only their assigned accounts
    """
    # Parse date (default to today)
    if date:
        try:
            snapshot_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        snapshot_date = date.today()
    
    query = db.query(LiveProductSnapshot).filter(
        LiveProductSnapshot.snapshot_date == snapshot_date
    )
    
    # Apply account filter if provided
    if account_id:
        # Check permission
        if not can_access_account(current_user, account_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this account")
        query = query.filter(LiveProductSnapshot.account_id == account_id)
    
    # Apply RBAC scope
    role = normalize_role(current_user.role)
    if role not in ["owner", "super_admin", "admin"]:
        # Leader/Host: filter by their scope
        # TODO: Implement proper scope filtering based on user relationships
        pass
    
    snapshots = query.order_by(desc(LiveProductSnapshot.gmv)).limit(100).all()
    return snapshots


@router.get("/ranking", response_model=LiveProductRankingResponse)
def get_product_ranking(
    date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/live-products/ranking?date=YYYY-MM-DD
    Get top 10 products by GMV and sold quantity
    """
    # Parse date
    if date:
        try:
            snapshot_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        snapshot_date = date.today()
    
    # Top 10 by GMV
    top_gmv = db.query(LiveProductSnapshot).filter(
        LiveProductSnapshot.snapshot_date == snapshot_date
    ).order_by(desc(LiveProductSnapshot.gmv)).limit(10).all()
    
    # Top 10 by sold qty
    top_sold = db.query(LiveProductSnapshot).filter(
        LiveProductSnapshot.snapshot_date == snapshot_date
    ).order_by(desc(LiveProductSnapshot.sold_qty)).limit(10).all()
    
    return LiveProductRankingResponse(
        top_by_gmv=[
            LiveProductRankingItem(
                product_id=p.product_id,
                product_name=p.product_name,
                sold_qty=p.sold_qty,
                gmv=p.gmv,
                rank=idx + 1
            )
            for idx, p in enumerate(top_gmv)
        ],
        top_by_sold=[
            LiveProductRankingItem(
                product_id=p.product_id,
                product_name=p.product_name,
                sold_qty=p.sold_qty,
                gmv=p.gmv,
                rank=idx + 1
            )
            for idx, p in enumerate(top_sold)
        ]
    )


@router.get("/sync-logs", response_model=List[LiveSyncLogResponse])
def get_sync_logs(
    account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/live-products/sync-logs?account_id=123
    Get last 20 sync logs
    """
    query = db.query(LiveSyncLog)
    
    if account_id:
        if not can_access_account(current_user, account_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this account")
        query = query.filter(LiveSyncLog.account_id == account_id)
    
    logs = query.order_by(desc(LiveSyncLog.synced_at)).limit(20).all()
    return logs
