"""
Supabase Integration: Process data from shopee_data_sync staging table
This endpoint processes data that was inserted directly by extension to Supabase
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order
from app.routes.shopee_data_sync import (
    process_identity_sync,
    process_transactions_sync,
    process_affiliate_dashboard_sync,
    process_live_streaming_sync
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shopee-data", tags=["Shopee Data Sync"])


@router.post("/process-pending")
async def process_pending_syncs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process pending syncs from shopee_data_sync table.
    This is called periodically by backend to process data inserted by extension directly to Supabase.
    
    **Permissions:** Admin only
    """
    if current_user.role not in ['super_admin', 'admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get pending records from staging table
    query = text("""
        SELECT id, type, account_info, payload, access_code, created_at
        FROM shopee_data_sync
        WHERE processed = FALSE
        ORDER BY created_at ASC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    pending_records = result.fetchall()
    
    processed_count = 0
    error_count = 0
    errors = []
    
    for record in pending_records:
        try:
            # Convert to dict format
            data = {
                "type": record.type,
                "account": record.account_info or {},
                "data": record.payload or {}
            }
            
            # Process based on type
            if record.type == "identity":
                await process_identity_sync(data, record.access_code, db)
            elif record.type == "transactions":
                await process_transactions_sync(data, record.access_code, db)
            elif record.type == "affiliate_dashboard":
                await process_affiliate_dashboard_sync(data, record.access_code, db)
            elif record.type == "live_streaming":
                await process_live_streaming_sync(data, record.access_code, db)
            else:
                logger.warning(f"Unknown sync type: {record.type}")
                continue
            
            # Mark as processed
            update_query = text("""
                UPDATE shopee_data_sync
                SET processed = TRUE, processed_at = NOW()
                WHERE id = :id
            """)
            db.execute(update_query, {"id": record.id})
            db.commit()
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing sync {record.id}: {str(e)}")
            error_count += 1
            errors.append({
                "id": record.id,
                "error": str(e)
            })
            
            # Mark with error
            update_query = text("""
                UPDATE shopee_data_sync
                SET error_message = :error
                WHERE id = :id
            """)
            db.execute(update_query, {"id": record.id, "error": str(e)})
            db.commit()
    
    return {
        "success": True,
        "processed": processed_count,
        "errors": error_count,
        "error_details": errors
    }


@router.get("/pending-count")
async def get_pending_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of pending syncs"""
    if current_user.role not in ['super_admin', 'admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = text("SELECT COUNT(*) as count FROM shopee_data_sync WHERE processed = FALSE")
    result = db.execute(query)
    count = result.fetchone().count
    
    return {
        "pending_count": count
    }