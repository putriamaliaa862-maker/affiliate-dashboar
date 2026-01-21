"""
Realtime Snapshot Schemas - For 24H Playwright Bot API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SnapshotType(str, Enum):
    CREATOR_LIVE = "creator_live"
    ADS = "ads"
    COINS = "coins"
    SUMMARY = "summary"


# ==================== REQUEST SCHEMAS ====================

class IngestSnapshotRequest(BaseModel):
    """Request body for ingesting a single snapshot"""
    shopee_account_id: str = Field(..., min_length=1, max_length=100)
    shop_name: Optional[str] = Field(None, max_length=255)
    snapshot_type: SnapshotType
    data: Dict[str, Any]
    scraped_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "shopee_account_id": "affiliate_123456",
                "shop_name": "YEYEP STORE",
                "snapshot_type": "creator_live",
                "data": {
                    "orders_ready_to_ship": 15,
                    "pending_orders": 3,
                    "total_orders_today": 25
                },
                "scraped_at": "2026-01-18T18:00:00Z"
            }
        }


class IngestBatchRequest(BaseModel):
    """Request body for ingesting multiple snapshots"""
    snapshots: List[IngestSnapshotRequest]


# ==================== RESPONSE SCHEMAS ====================

class IngestSnapshotResponse(BaseModel):
    """Response after ingesting a snapshot"""
    success: bool
    snapshot_id: int
    message: str = "Snapshot ingested successfully"


class IngestBatchResponse(BaseModel):
    """Response after ingesting batch of snapshots"""
    success: bool
    total: int
    ingested: int
    failed: int
    message: str


class SnapshotOut(BaseModel):
    """Output schema for a single snapshot"""
    id: int
    shopee_account_id: str
    shop_name: Optional[str]
    snapshot_type: str
    data: Dict[str, Any]
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SnapshotListResponse(BaseModel):
    """Response for listing snapshots"""
    success: bool
    total: int
    snapshots: List[SnapshotOut]


# ==================== BOT RUN SCHEMAS ====================

class BotRunOut(BaseModel):
    """Output schema for bot run status"""
    id: int
    run_id: str
    status: str
    accounts_total: int
    accounts_processed: int
    accounts_success: int
    accounts_failed: int
    error_message: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class BotRunListResponse(BaseModel):
    """Response for listing bot runs"""
    success: bool
    runs: List[BotRunOut]


# ==================== DASHBOARD AGGREGATION ====================

class CreatorLiveOverview(BaseModel):
    """Aggregated view for Creator Live dashboard"""
    total_accounts: int
    total_orders_ready: int
    total_pending: int
    last_updated: Optional[datetime]
    accounts: List[Dict[str, Any]]


class AdsOverview(BaseModel):
    """Aggregated view for Ads dashboard"""
    total_accounts: int
    total_spend_today: float
    total_budget_available: float
    total_coins: float
    last_updated: Optional[datetime]
    accounts: List[Dict[str, Any]]
