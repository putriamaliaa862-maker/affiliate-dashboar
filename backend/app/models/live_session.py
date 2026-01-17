"""
Live Session Model - Menyimpan data live streaming session
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base


class LiveSession(Base):
    """Model untuk menyimpan live streaming session data"""
    
    __tablename__ = "live_sessions"
    
    id = Column(Integer, primary_key=True)
    studio_id = Column(Integer, nullable=False)  # Reference ke studio
    shopee_account_id = Column(Integer, nullable=False)  # Reference ke shopee account
    
    # Session Info
    session_id = Column(String(255), unique=True, nullable=False)
    session_name = Column(String(255), nullable=False)
    streamer_id = Column(String(255))
    streamer_name = Column(String(255))
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer, default=0)
    
    # Live Status
    status = Column(String(50), default="ongoing")  # ongoing, ended, scheduled
    is_live = Column(Boolean, default=True)
    
    # Metrics
    total_viewers = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_comments = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Products
    products_count = Column(Integer, default=0)
    items_promoted = Column(JSON, default={})  # {item_id: {name, price, sold}}
    
    # Campaign
    campaign_id = Column(String(255))
    campaign_name = Column(String(255))
    campaign_budget = Column(Float, default=0.0)
    campaign_spent = Column(Float, default=0.0)
    
    # Engagement
    coins_distributed = Column(Integer, default=0)
    coin_total_value = Column(Float, default=0.0)
    
    # Extra Data
    extra_data = Column(JSON, default={})  # Untuk data tambahan
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    synced_at = Column(DateTime)  # Last sync dari Shopee API
    
    def __repr__(self):
        return f"<LiveSession {self.session_name} ({self.status})>"
