"""
Live Analytics Model - Analytics data untuk live streaming
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class LiveAnalytics(Base):
    """Model untuk menyimpan analytics live streaming"""
    
    __tablename__ = "live_analytics"
    
    id = Column(Integer, primary_key=True)
    
    # Reference
    studio_id = Column(Integer, nullable=False)
    live_session_id = Column(String(255), nullable=False)
    
    # Daily Stats
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    
    # Viewer Metrics
    total_sessions_count = Column(Integer, default=0)
    average_viewers = Column(Float, default=0.0)
    peak_viewers = Column(Integer, default=0)
    total_watch_time_minutes = Column(Integer, default=0)
    
    # Sales Metrics
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)  # orders / viewers
    
    # Engagement Metrics
    total_comments = Column(Integer, default=0)
    average_comments_per_session = Column(Float, default=0.0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Product Metrics
    unique_products_promoted = Column(Integer, default=0)
    top_product = Column(String(500))  # top selling product name
    
    # Finance
    total_ad_spend = Column(Float, default=0.0)
    total_commission = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)  # (revenue - spend) / spend * 100
    
    # Streamer/Creator Stats
    top_streamer = Column(String(255))
    streamer_count = Column(Integer, default=0)
    
    # Raw Data
    detailed_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LiveAnalytics {self.date} - {self.total_revenue}>"
