"""
Live Streaming Schemas - Pydantic models untuk live streaming
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class LiveSessionCreate(BaseModel):
    """Schema untuk create live session"""
    studio_id: int
    shopee_account_id: int
    session_id: str
    session_name: str
    streamer_id: Optional[str] = None
    streamer_name: Optional[str] = None
    status: str = "ongoing"
    
    class Config:
        from_attributes = True


class LiveSessionUpdate(BaseModel):
    """Schema untuk update live session"""
    session_name: Optional[str] = None
    status: Optional[str] = None
    total_viewers: Optional[int] = None
    peak_viewers: Optional[int] = None
    total_orders: Optional[int] = None
    total_revenue: Optional[float] = None
    total_comments: Optional[int] = None
    total_likes: Optional[int] = None
    total_shares: Optional[int] = None
    products_count: Optional[int] = None
    coins_distributed: Optional[int] = None
    coin_total_value: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class LiveSessionResponse(BaseModel):
    """Schema response untuk live session"""
    id: int
    studio_id: int
    shopee_account_id: int
    session_id: str
    session_name: str
    streamer_id: Optional[str]
    streamer_name: Optional[str]
    status: str
    is_live: bool
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_viewers: int
    peak_viewers: int
    total_orders: int
    total_revenue: float
    total_comments: int
    total_likes: int
    total_shares: int
    products_count: int
    campaign_id: Optional[str]
    campaign_name: Optional[str]
    campaign_budget: float
    campaign_spent: float
    coins_distributed: int
    coin_total_value: float
    created_at: datetime
    updated_at: datetime
    synced_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LiveSessionItemCreate(BaseModel):
    """Schema untuk create live session item"""
    live_session_id: int
    item_id: str
    product_name: str
    regular_price: Optional[float] = None
    live_price: Optional[float] = None
    discount_percentage: Optional[float] = 0.0
    
    class Config:
        from_attributes = True


class LiveSessionItemResponse(BaseModel):
    """Schema response untuk live session item"""
    id: int
    live_session_id: int
    item_id: str
    product_name: str
    product_image_url: Optional[str]
    regular_price: Optional[float]
    live_price: Optional[float]
    discount_percentage: float
    quantity_sold: int
    total_sales_amount: float
    commission_per_item: float
    total_commission: float
    promotion_type: Optional[str]
    is_featured: str
    promoted_at: Optional[datetime]
    last_updated: datetime
    
    class Config:
        from_attributes = True


class LiveAnalyticsCreate(BaseModel):
    """Schema untuk create live analytics"""
    studio_id: int
    live_session_id: str
    date: str  # YYYY-MM-DD
    total_sessions_count: int = 0
    average_viewers: float = 0.0
    peak_viewers: int = 0
    total_watch_time_minutes: int = 0
    total_orders: int = 0
    total_revenue: float = 0.0
    average_order_value: float = 0.0
    conversion_rate: float = 0.0
    total_comments: int = 0
    average_comments_per_session: float = 0.0
    total_likes: int = 0
    total_shares: int = 0
    unique_products_promoted: int = 0
    top_product: Optional[str] = None
    total_ad_spend: float = 0.0
    total_commission: float = 0.0
    roi_percentage: float = 0.0
    top_streamer: Optional[str] = None
    streamer_count: int = 0
    detailed_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class LiveAnalyticsResponse(BaseModel):
    """Schema response untuk live analytics"""
    id: int
    studio_id: int
    live_session_id: str
    date: str
    total_sessions_count: int
    average_viewers: float
    peak_viewers: int
    total_watch_time_minutes: int
    total_orders: int
    total_revenue: float
    average_order_value: float
    conversion_rate: float
    total_comments: int
    average_comments_per_session: float
    total_likes: int
    total_shares: int
    unique_products_promoted: int
    top_product: Optional[str]
    total_ad_spend: float
    total_commission: float
    roi_percentage: float
    top_streamer: Optional[str]
    streamer_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SyncLiveSessionRequest(BaseModel):
    """Schema untuk sync live session request"""
    session_id: str
    studio_id: int
    shopee_account_id: int
    access_token: str
    
    class Config:
        from_attributes = True


class CreatorUserInfoResponse(BaseModel):
    """Response dari creator user info API"""
    user_id: str
    username: str
    shop_id: str
    shop_name: str
    follower_count: int
    following_count: int
    
    class Config:
        from_attributes = True


class LiveSessionListResponse(BaseModel):
    """Response dari session list API"""
    sessions: list
    total: int
    
    class Config:
        from_attributes = True
