"""
Pydantic schemas for Live Product Snapshot API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import date, datetime


# ==================== Request Schemas ====================

class ProductSyncItem(BaseModel):
    """Individual product data for sync"""
    product_id: str
    product_name: str
    sold_qty: int = 0
    gmv: float = 0.0
    clicks: Optional[int] = 0


class LiveProductSyncRequest(BaseModel):
    """Payload for syncing live product data"""
    account_id: int
    snapshot_date: str  # YYYY-MM-DD format
    source: str = "live"  # 'live', 'manual', 'extension'
    products: List[ProductSyncItem]
    raw_data: Optional[dict] = None


# ==================== Response Schemas ====================

class LiveProductSyncResponse(BaseModel):
    """Response after sync operation"""
    success: bool
    inserted: int
    updated: int
    total: int
    message: Optional[str] = None


class LiveProductSnapshotResponse(BaseModel):
    """Single product snapshot"""
    id: int
    snapshot_date: date
    account_id: int
    studio_id: Optional[int]
    leader_id: Optional[int]
    host_id: Optional[int]
    product_id: str
    product_name: str
    sold_qty: int
    gmv: float
    clicks: Optional[int]
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LiveProductRankingItem(BaseModel):
    """Top product ranking item"""
    product_id: str
    product_name: str
    sold_qty: int
    gmv: float
    rank: int


class LiveProductRankingResponse(BaseModel):
    """Top products ranking"""
    top_by_gmv: List[LiveProductRankingItem]
    top_by_sold: List[LiveProductRankingItem]


class LiveSyncLogResponse(BaseModel):
    """Sync log entry"""
    id: int
    account_id: int
    snapshot_date: date
    synced_at: datetime
    status: str
    total_rows: int
    message: Optional[str]
    
    class Config:
        from_attributes = True
