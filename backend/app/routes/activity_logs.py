"""
Activity log routes for viewing audit trail.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/activity-logs", tags=["Activity Logs"])


@router.get("")
async def list_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    List activity logs with filtering.
    
    **Permissions:** Admin or higher
    
    - **user_id**: Filter by user
    - **action**: Filter by action type
    - **entity_type**: Filter by entity (user, employee, etc.)
    - **date_from**: Start date
    - **date_to**: End date
    """
    query = db.query(ActivityLog)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    if action:
        query = query.filter(ActivityLog.action == action)
    
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    
    if date_from:
        query = query.filter(ActivityLog.created_at >= date_from)
    
    if date_to:
        query = query.filter(ActivityLog.created_at <= date_to)
    
    logs = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [log.to_dict() for log in logs]


@router.get("/user/{user_id}")
async def get_user_activity_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity logs for a specific user.
    
    **Permissions:**
    - Users can view their own logs
    - Admins can view any user's logs
    """
    # Check permissions
    if current_user.id != user_id and current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id
    ).order_by(
        ActivityLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [log.to_dict() for log in logs]
