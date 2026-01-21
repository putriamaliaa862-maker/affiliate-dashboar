"""
Bot Ingest Routes - API endpoints for 24H Playwright Bot
Handles realtime snapshot ingestion and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.auth.access_code import verify_access_code
from app.models.user import User
from app.models.realtime_snapshot import RealtimeSnapshot, BotRun
from app.schemas.realtime_snapshot import (
    IngestSnapshotRequest,
    IngestSnapshotResponse,
    IngestBatchRequest,
    IngestBatchResponse,
    SnapshotOut,
    SnapshotListResponse,
    BotRunOut,
    BotRunListResponse,
    CreatorLiveOverview,
    AdsOverview,
    SnapshotType
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bot", tags=["Bot Ingest"])


# ==================== INGEST ENDPOINTS ====================

@router.post("/realtime-snapshots/ingest", response_model=IngestSnapshotResponse)
async def ingest_snapshot(
    payload: IngestSnapshotRequest,
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """
    Ingest a single realtime snapshot from Playwright bot.
    Auth: X-Access-Code header
    """
    print("=" * 60)
    print("🤖 BOT INGEST HIT")
    print(f"User ID: {current_user.id}")
    print(f"Account: {payload.shopee_account_id}")
    print(f"Type: {payload.snapshot_type}")
    print(f"Shop: {payload.shop_name}")
    print("=" * 60)
    
    try:
        snapshot = RealtimeSnapshot(
            shopee_account_id=payload.shopee_account_id,
            shop_name=payload.shop_name,
            snapshot_type=payload.snapshot_type.value,
            data=payload.data,
            scraped_at=payload.scraped_at
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        logger.info(f"[BotIngest] Snapshot {snapshot.id} ingested for {payload.shopee_account_id}")
        
        return IngestSnapshotResponse(
            success=True,
            snapshot_id=snapshot.id,
            message=f"Snapshot ingested for {payload.shopee_account_id}"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"[BotIngest] Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest snapshot: {str(e)}"
        )


@router.post("/realtime-snapshots/ingest-batch", response_model=IngestBatchResponse)
async def ingest_batch(
    payload: IngestBatchRequest,
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """Ingest multiple snapshots in one request"""
    print(f"🤖 BOT BATCH INGEST: {len(payload.snapshots)} snapshots")
    
    ingested = 0
    failed = 0
    
    for snap in payload.snapshots:
        try:
            snapshot = RealtimeSnapshot(
                shopee_account_id=snap.shopee_account_id,
                shop_name=snap.shop_name,
                snapshot_type=snap.snapshot_type.value,
                data=snap.data,
                scraped_at=snap.scraped_at
            )
            db.add(snapshot)
            ingested += 1
        except Exception as e:
            logger.error(f"[BotIngest] Batch error for {snap.shopee_account_id}: {e}")
            failed += 1
    
    db.commit()
    
    return IngestBatchResponse(
        success=failed == 0,
        total=len(payload.snapshots),
        ingested=ingested,
        failed=failed,
        message=f"Ingested {ingested}/{len(payload.snapshots)} snapshots"
    )


# ==================== QUERY ENDPOINTS ====================

@router.get("/realtime-snapshots", response_model=SnapshotListResponse)
async def list_snapshots(
    snapshot_type: Optional[str] = Query(None, description="Filter by type"),
    account_id: Optional[str] = Query(None, description="Filter by account"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """List realtime snapshots with optional filters"""
    query = db.query(RealtimeSnapshot)
    
    if snapshot_type:
        query = query.filter(RealtimeSnapshot.snapshot_type == snapshot_type)
    if account_id:
        query = query.filter(RealtimeSnapshot.shopee_account_id == account_id)
    
    total = query.count()
    snapshots = query.order_by(desc(RealtimeSnapshot.scraped_at)).offset(offset).limit(limit).all()
    
    return SnapshotListResponse(
        success=True,
        total=total,
        snapshots=[SnapshotOut.model_validate(s) for s in snapshots]
    )


@router.get("/realtime-snapshots/latest")
async def get_latest_snapshots(
    snapshot_type: Optional[str] = Query(None),
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """Get latest snapshot per account (for dashboard overview)"""
    # Subquery to get max scraped_at per account per type
    subq = db.query(
        RealtimeSnapshot.shopee_account_id,
        func.max(RealtimeSnapshot.scraped_at).label('max_scraped')
    ).group_by(RealtimeSnapshot.shopee_account_id)
    
    if snapshot_type:
        subq = subq.filter(RealtimeSnapshot.snapshot_type == snapshot_type)
    
    subq = subq.subquery()
    
    # Join with main table to get full records
    query = db.query(RealtimeSnapshot).join(
        subq,
        (RealtimeSnapshot.shopee_account_id == subq.c.shopee_account_id) &
        (RealtimeSnapshot.scraped_at == subq.c.max_scraped)
    )
    
    if snapshot_type:
        query = query.filter(RealtimeSnapshot.snapshot_type == snapshot_type)
    
    snapshots = query.all()
    
    return {
        "success": True,
        "total": len(snapshots),
        "snapshots": [SnapshotOut.model_validate(s) for s in snapshots]
    }


# ==================== DASHBOARD AGGREGATION ====================

@router.get("/dashboard/creator-live", response_model=CreatorLiveOverview)
async def get_creator_live_overview(
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """Get aggregated Creator Live overview for dashboard"""
    # Get latest snapshots for creator_live type
    subq = db.query(
        RealtimeSnapshot.shopee_account_id,
        func.max(RealtimeSnapshot.scraped_at).label('max_scraped')
    ).filter(
        RealtimeSnapshot.snapshot_type == 'creator_live'
    ).group_by(RealtimeSnapshot.shopee_account_id).subquery()
    
    snapshots = db.query(RealtimeSnapshot).join(
        subq,
        (RealtimeSnapshot.shopee_account_id == subq.c.shopee_account_id) &
        (RealtimeSnapshot.scraped_at == subq.c.max_scraped)
    ).filter(RealtimeSnapshot.snapshot_type == 'creator_live').all()
    
    total_orders_ready = 0
    total_pending = 0
    accounts = []
    last_updated = None
    
    for snap in snapshots:
        data = snap.data or {}
        total_orders_ready += data.get('orders_ready_to_ship', 0)
        total_pending += data.get('pending_orders', 0)
        
        accounts.append({
            "shopee_account_id": snap.shopee_account_id,
            "shop_name": snap.shop_name,
            "orders_ready_to_ship": data.get('orders_ready_to_ship', 0),
            "pending_orders": data.get('pending_orders', 0),
            "scraped_at": snap.scraped_at.isoformat() if snap.scraped_at else None
        })
        
        if not last_updated or (snap.scraped_at and snap.scraped_at > last_updated):
            last_updated = snap.scraped_at
    
    return CreatorLiveOverview(
        total_accounts=len(snapshots),
        total_orders_ready=total_orders_ready,
        total_pending=total_pending,
        last_updated=last_updated,
        accounts=accounts
    )


@router.get("/dashboard/ads", response_model=AdsOverview)
async def get_ads_overview(
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """Get aggregated Ads overview for dashboard"""
    subq = db.query(
        RealtimeSnapshot.shopee_account_id,
        func.max(RealtimeSnapshot.scraped_at).label('max_scraped')
    ).filter(
        RealtimeSnapshot.snapshot_type == 'ads'
    ).group_by(RealtimeSnapshot.shopee_account_id).subquery()
    
    snapshots = db.query(RealtimeSnapshot).join(
        subq,
        (RealtimeSnapshot.shopee_account_id == subq.c.shopee_account_id) &
        (RealtimeSnapshot.scraped_at == subq.c.max_scraped)
    ).filter(RealtimeSnapshot.snapshot_type == 'ads').all()
    
    total_spend = 0.0
    total_budget = 0.0
    total_coins = 0.0
    accounts = []
    last_updated = None
    
    for snap in snapshots:
        data = snap.data or {}
        total_spend += float(data.get('spend_today', 0))
        total_budget += float(data.get('budget_available', 0))
        total_coins += float(data.get('coins', 0))
        
        accounts.append({
            "shopee_account_id": snap.shopee_account_id,
            "shop_name": snap.shop_name,
            "spend_today": data.get('spend_today', 0),
            "budget_available": data.get('budget_available', 0),
            "coins": data.get('coins', 0),
            "scraped_at": snap.scraped_at.isoformat() if snap.scraped_at else None
        })
        
        if not last_updated or (snap.scraped_at and snap.scraped_at > last_updated):
            last_updated = snap.scraped_at
    
    return AdsOverview(
        total_accounts=len(snapshots),
        total_spend_today=total_spend,
        total_budget_available=total_budget,
        total_coins=total_coins,
        last_updated=last_updated,
        accounts=accounts
    )


# ==================== BOT STATUS ====================

@router.get("/runs", response_model=BotRunListResponse)
async def list_bot_runs(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """List recent bot runs"""
    runs = db.query(BotRun).order_by(desc(BotRun.started_at)).limit(limit).all()
    
    return BotRunListResponse(
        success=True,
        runs=[BotRunOut.model_validate(r) for r in runs]
    )


@router.get("/status")
async def get_bot_status(
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """Get current bot status based on recent snapshots"""
    # Check if we have snapshots in last 5 minutes
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    
    recent_count = db.query(RealtimeSnapshot).filter(
        RealtimeSnapshot.scraped_at >= five_min_ago
    ).count()
    
    latest = db.query(RealtimeSnapshot).order_by(
        desc(RealtimeSnapshot.scraped_at)
    ).first()
    
    is_active = recent_count > 0
    
    return {
        "success": True,
        "is_active": is_active,
        "status": "active" if is_active else "inactive",
        "recent_snapshots_count": recent_count,
        "last_snapshot_at": latest.scraped_at.isoformat() if latest else None,
        "message": "Bot is running" if is_active else "No recent snapshots (>5 min)"
    }
