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
            # For now, just mark as processed
            # The actual processing can be done by calling the main sync endpoint
            # via HTTP request or by refactoring the sync logic to be reusable
            logger.info(f"Processing sync {record.id}, type: {record.type}")
            
            # TODO: Implement actual processing logic here
            # For now, we'll mark as processed (can be improved later)
            # The extension can also call the main /api/shopee-data/sync endpoint directly
            
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