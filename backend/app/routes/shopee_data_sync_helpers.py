"""
Helper function to process live streaming data
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _process_live_streaming(db: Session, account_id: int, data: Dict[str, Any]) -> int:
    """
    Process live streaming metrics and save to database.
    
    Args:
        db: Database session
        account_id: Shopee account ID
        data: Payload data containing live_streaming metrics
    
    Returns:
        Number of rows saved
    """
    live_data = data.get('live_streaming', {}) or data
    
    if not live_data or not isinstance(live_data, dict):
        logger.warning(f"[ProcessLive] No live streaming data found")
        return 0
    
    # For now, just log the data (TODO: Create live_sessions table)
    logger.info(f"[ProcessLive] Live data for account_id={account_id}: {live_data}")
    
    # Extract metrics
    viewers = live_data.get('viewers', 0)
    likes = live_data.get('likes', 0)
    total_sales = live_data.get('totalSales', 0) or live_data.get('total_sales', 0)
    revenue = live_data.get('revenue', 0)
    duration = live_data.get('duration', '0:00')
    
    logger.info(f"[ProcessLive] Metrics - viewers={viewers}, sales={total_sales}, revenue={revenue}")
    
    # TODO: Save to live_sessions or live_metrics table when schema is ready
    # For now, just return 1 to indicate data was processed
    return 1 if any([viewers, likes, total_sales, revenue]) else 0
