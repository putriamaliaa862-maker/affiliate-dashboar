"""
Live Streaming Routes - API endpoints untuk live streaming integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.live_session import LiveSession
from app.models.live_session_item import LiveSessionItem
from app.models.live_analytics import LiveAnalytics
from app.services.shopee_streaming import shopee_streaming_service
from app.schemas.live import (
    LiveSessionCreate,
    LiveSessionUpdate,
    LiveSessionResponse,
    LiveAnalyticsResponse,
    SyncLiveSessionRequest,
)

router = APIRouter(prefix="/api/live-streaming", tags=["live-streaming"])


# ==================== LIVE SESSION CRUD ====================

@router.get("/sessions", response_model=List[LiveSessionResponse])
async def list_live_sessions(
    studio_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """List semua live sessions dengan filter"""
    query = db.query(LiveSession)
    
    if studio_id:
        query = query.filter(LiveSession.studio_id == studio_id)
    if status:
        query = query.filter(LiveSession.status == status)
    
    sessions = query.offset(skip).limit(limit).all()
    return sessions


@router.post("/sessions", response_model=LiveSessionResponse)
async def create_live_session(
    session_data: LiveSessionCreate,
    db: Session = Depends(get_db),
):
    """Create new live session record"""
    db_session = LiveSession(**session_data.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=LiveSessionResponse)
async def get_live_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get detail live session"""
    db_session = db.query(LiveSession).filter(LiveSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put("/sessions/{session_id}", response_model=LiveSessionResponse)
async def update_live_session(
    session_id: str,
    session_data: LiveSessionUpdate,
    db: Session = Depends(get_db),
):
    """Update live session"""
    db_session = db.query(LiveSession).filter(LiveSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = session_data.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/sessions/{session_id}")
async def delete_live_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Delete live session"""
    db_session = db.query(LiveSession).filter(LiveSession.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    
    return {"message": "Session deleted successfully"}


# ==================== LIVE SESSION SYNC ====================

@router.post("/sessions/sync")
async def sync_live_session(
    sync_data: SyncLiveSessionRequest,
    db: Session = Depends(get_db),
):
    """
    Sync live session data dari Shopee API
    Endpoint ini akan fetch latest data dan update database
    """
    try:
        # Get session info dari Shopee
        session_info = await shopee_streaming_service.get_session_info(
            sync_data.session_id,
            sync_data.access_token
        )
        
        # Get dashboard overview
        dashboard = await shopee_streaming_service.get_dashboard_overview(
            sync_data.session_id,
            sync_data.access_token
        )
        
        # Get items/products
        items = await shopee_streaming_service.get_item_promotion_list(
            access_token=sync_data.access_token
        )
        
        # Update atau create session di DB
        db_session = db.query(LiveSession).filter(
            LiveSession.session_id == sync_data.session_id
        ).first()
        
        if not db_session:
            db_session = LiveSession(
                session_id=sync_data.session_id,
                studio_id=sync_data.studio_id,
                shopee_account_id=sync_data.shopee_account_id,
                session_name=session_info.get("name", ""),
                streamer_id=session_info.get("streamer_id", ""),
                streamer_name=session_info.get("streamer_name", ""),
            )
            db.add(db_session)
        
        # Update metrics dari dashboard
        db_session.total_viewers = dashboard.get("total_viewers", 0)
        db_session.peak_viewers = dashboard.get("peak_viewers", 0)
        db_session.total_orders = dashboard.get("total_orders", 0)
        db_session.total_revenue = dashboard.get("total_revenue", 0.0)
        db_session.total_comments = dashboard.get("total_comments", 0)
        db_session.total_likes = dashboard.get("total_likes", 0)
        db_session.total_shares = dashboard.get("total_shares", 0)
        db_session.products_count = len(items.get("items", []))
        db_session.synced_at = datetime.utcnow()
        db_session.extra_data = {
            "session_info": session_info,
            "dashboard": dashboard,
        }
        
        db.commit()
        db.refresh(db_session)
        
        return {
            "status": "success",
            "session_id": sync_data.session_id,
            "data": {
                "session": db_session,
                "synced_at": db_session.synced_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")


# ==================== LIVE ANALYTICS ====================

@router.get("/analytics", response_model=List[LiveAnalyticsResponse])
async def get_live_analytics(
    studio_id: int = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get live streaming analytics"""
    query = db.query(LiveAnalytics).filter(LiveAnalytics.studio_id == studio_id)
    
    if start_date:
        query = query.filter(LiveAnalytics.date >= start_date)
    if end_date:
        query = query.filter(LiveAnalytics.date <= end_date)
    
    analytics = query.order_by(LiveAnalytics.date.desc()).all()
    return analytics


@router.get("/analytics/summary")
async def get_analytics_summary(
    studio_id: int = Query(...),
    days: int = Query(30),
    db: Session = Depends(get_db),
):
    """Get aggregated analytics summary"""
    from sqlalchemy import func
    
    analytics = db.query(LiveAnalytics).filter(
        LiveAnalytics.studio_id == studio_id
    ).order_by(LiveAnalytics.date.desc()).limit(days).all()
    
    if not analytics:
        return {
            "total_sessions": 0,
            "total_revenue": 0.0,
            "total_viewers": 0,
            "average_order_value": 0.0,
            "conversion_rate": 0.0,
            "roi_percentage": 0.0,
        }
    
    total_sessions = sum(a.total_sessions_count for a in analytics)
    total_revenue = sum(a.total_revenue for a in analytics)
    total_viewers = sum(int(a.average_viewers) for a in analytics)
    average_order_value = sum(a.average_order_value for a in analytics) / len(analytics) if analytics else 0
    conversion_rate = sum(a.conversion_rate for a in analytics) / len(analytics) if analytics else 0
    roi_percentage = sum(a.roi_percentage for a in analytics) / len(analytics) if analytics else 0
    
    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "total_revenue": total_revenue,
        "total_viewers": total_viewers,
        "average_order_value": average_order_value,
        "conversion_rate": conversion_rate,
        "roi_percentage": roi_percentage,
    }


# ==================== SHOPEE API PROXY ====================

@router.post("/creator/user-info")
async def get_creator_user_info(
    access_token: str = Query(...),
):
    """Get creator user info dari Shopee"""
    try:
        user_info = await shopee_streaming_service.get_creator_user_info(access_token)
        return {"status": "success", "data": user_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/creator/session-list")
async def get_session_list(
    access_token: str = Query(...),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """Get creator session list dari Shopee"""
    try:
        sessions = await shopee_streaming_service.get_session_list(
            access_token=access_token,
            page=page,
            page_size=page_size
        )
        return {"status": "success", "data": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promotions/today")
async def get_promotions_today(
    access_token: str = Query(...),
):
    """Get promotions hari ini dari Shopee"""
    try:
        promotions = await shopee_streaming_service.get_promotions_today(access_token)
        return {"status": "success", "data": promotions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/expense-today")
async def get_campaign_expense_today(
    access_token: str = Query(...),
):
    """Get campaign expense hari ini dari Shopee"""
    try:
        expense = await shopee_streaming_service.get_campaign_expense_today(access_token)
        return {"status": "success", "data": expense}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ads-data")
async def get_ads_data(
    access_token: str = Query(...),
):
    """Get meta ads data dari Shopee"""
    try:
        ads_data = await shopee_streaming_service.get_ads_data(access_token)
        return {"status": "success", "data": ads_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/promotion")
async def get_item_promotion_list(
    access_token: str = Query(...),
    offset: int = Query(0),
    limit: int = Query(50),
):
    """Get item promotion list dari Shopee"""
    try:
        items = await shopee_streaming_service.get_item_promotion_list(
            offset=offset,
            limit=limit,
            access_token=access_token
        )
        return {"status": "success", "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coin/giveout/{session_id}")
async def coin_giveout(
    session_id: str,
    coin_data: dict,
    access_token: str = Query(...),
):
    """Giveout coin dalam live session"""
    try:
        result = await shopee_streaming_service.coin_giveout(
            session_id=session_id,
            coin_data=coin_data,
            access_token=access_token
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@router.get("/share-link/{session_id}")
async def get_live_share_link(session_id: str):
    """Get share link untuk live session"""
    share_link = shopee_streaming_service.get_live_share_link(session_id)
    return {"share_link": share_link}


@router.get("/product-url")
async def get_product_url(
    shop_id: str = Query(...),
    item_id: str = Query(...),
):
    """Build product URL"""
    product_url = shopee_streaming_service.get_product_url(shop_id, item_id)
    return {"product_url": product_url}
